from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.db.models import CanonicalTransaction, Exception, Resolution, ResolutionStatus, ExceptionType, AuditLog, AuditAction, TransactionSource
from backend.app.schemas.canonical import AIResolution
from backend.app.services.llm_providers import LLMProvider, get_provider, LLMMessage
from backend.app.config import get_settings, AIConfig
from pydantic import ValidationError


INVESTIGATOR_SYSTEM_PROMPT = """You are an AI Finance Investigator. Your job is to investigate financial reconciliation exceptions by examining evidence from multiple sources.

You have access to tools to retrieve transaction data. Use them to gather evidence before making a decision.

RULES:
1. NEVER fabricate evidence. Only use what you retrieve via tools.
2. If evidence is insufficient, return status "unresolved" or "escalated" with low confidence.
3. Be precise: classify as processor_fee, amount_mismatch, date_mismatch, duplicate, missing_record, etc.
4. Always cite specific evidence (amounts, dates, references) in your explanation.
5. Confidence must reflect evidence quality: 0.9+ for clear fee patterns, 0.7-0.8 for probable matches, <0.5 for ambiguous.

OUTPUT FORMAT (JSON):
{
  "status": "resolved|escalated|unresolved",
  "classification": "exception_type",
  "confidence": 0.0-1.0,
  "explanation": "Detailed reasoning with evidence citations",
  "evidence": ["evidence1", "evidence2"],
  "recommended_action": "action_description"
}"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_transaction",
            "description": "Get canonical transaction by ID",
            "parameters": {
                "type": "object",
                "properties": {"transaction_id": {"type": "integer"}},
                "required": ["transaction_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_source_records",
            "description": "Get all source records (bank, ledger, processor) for a canonical transaction",
            "parameters": {
                "type": "object",
                "properties": {"canonical_id": {"type": "integer"}},
                "required": ["canonical_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_similar",
            "description": "Search for similar transactions by amount, counterparty, date",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number"},
                    "counterparty": {"type": "string"},
                    "date_from": {"type": "string"},
                    "date_to": {"type": "string"},
                    "direction": {"type": "string"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_difference",
            "description": "Calculate differences between two transaction records",
            "parameters": {
                "type": "object",
                "properties": {
                    "record_a": {"type": "object"},
                    "record_b": {"type": "object"}
                },
                "required": ["record_a", "record_b"]
            }
        }
    }
]


class AIInvestigator:
    def __init__(self, config: AIConfig):
        self.config = config
        
        if config.provider == "ollama":
            self.provider = get_provider(
                "ollama",
                base_url=config.ollama.base_url,
                model=config.ollama.model,
                timeout=config.ollama.timeout,
            )
        elif config.provider == "groq":
            self.provider = get_provider(
                "groq",
                api_key=config.groq.api_key.get_secret_value() if config.groq.api_key else "",
                model=config.groq.model,
            )
        elif config.provider == "openai_compatible":
            self.provider = get_provider(
                "openai_compatible",
                base_url=config.openai_compatible.base_url or "",
                api_key=config.openai_compatible.api_key.get_secret_value() if config.openai_compatible.api_key else "",
                model=config.openai_compatible.model,
            )
        else:
            self.provider = get_provider("mock")

    async def investigate(self, db: AsyncSession, exception: Exception) -> Resolution:
        txn_result = await db.execute(select(CanonicalTransaction).where(CanonicalTransaction.id == exception.transaction_id))
        txn = txn_result.scalar_one_or_none()
        if not txn:
            raise ValueError(f"Transaction {exception.transaction_id} not found")

        messages = [
            LLMMessage(role="system", content=INVESTIGATOR_SYSTEM_PROMPT),
            LLMMessage(role="user", content=f"""
Investigate exception ID {exception.id}:
- Transaction: {txn.counterparty} | {txn.amount} {txn.currency} | {txn.date} | {txn.direction}
- Exception type: {exception.type}
- Current evidence: {exception.evidence}

Use tools to gather evidence from bank, ledger, and processor records.
Determine the root cause and classify the exception.
""")
        ]

        tool_results = []
        for _ in range(self.config.max_tool_calls):
            response = await self.provider.complete(messages, tools=TOOLS, tool_choice="auto")
            
            if response.tool_calls:
                for tool_call in response.tool_calls:
                    result = await self._execute_tool(db, tool_call)
                    tool_results.append(result)
                    messages.append(LLMMessage(role="tool", content=str(result.result), tool_calls=[tool_call]))
            else:
                break
        
        final_response = await self.provider.complete(messages, response_format={"type": "json_object"})
        
        import json
        ai_output = json.loads(final_response.content)
        ai_resolution = AIResolution(**ai_output)
        
        # Log AI classification proposed
        await self._log_audit(db, "AI_CLASSIFICATION_PROPOSED", exception.id, 
            f"AI proposed: {ai_resolution.classification.value} with confidence {ai_resolution.confidence:.2f}")
        
        # Validate AI resolution
        is_valid, error_msg = await self._validate_ai_resolution(db, ai_resolution, exception, txn)
        if not is_valid:
            # Log validation failure
            await self._log_audit(db, "AI_VALIDATION_FAILED", exception.id, f"Validation failed: {error_msg}")
            
            # If validation fails, escalate with low confidence
            ai_resolution.status = ResolutionStatus.ESCALATED
            ai_resolution.confidence = 0.1
            ai_resolution.explanation = f"Validation failed: {ai_resolution.explanation} (Validation error: {error_msg})"
            ai_resolution.status = ResolutionStatus.ESCALATED
            ai_resolution.confidence = 0.1
            ai_resolution.evidence = [f"Validation failed: {error_msg}"]
            ai_resolution.recommended_action = "Manual review required"
        else:
            # Log validation passed
            await self._log_audit(db, "AI_VALIDATION_PASSED", exception.id, 
                f"Validation passed for {ai_resolution.classification.value} with confidence {ai_resolution.confidence:.2f}")
        
        resolution = Resolution(
            exception_id=exception.id,
            status=ai_resolution.status,
            classification=ai_resolution.classification,
            confidence=ai_resolution.confidence,
            explanation=ai_resolution.explanation,
            evidence=ai_resolution.evidence,
            recommended_action=ai_resolution.recommended_action,
            validated=False,
        )
        
        await self._log_audit(db, "AI_INVESTIGATION_STARTED", exception.id, f"AI investigation for {exception.type}")
        
        # Save resolution to DB
        db.add(resolution)
        await db.commit()
        await db.refresh(resolution)
        
        # Log resolution saved
        await self._log_audit(db, "AI_RESOLUTION_SAVED", exception.id, 
            f"Resolution saved with status {resolution.status.value}, confidence {resolution.confidence:.2f}")
        
        return resolution

    async def _execute_tool(self, db: AsyncSession, tool_call) -> Any:
        name = tool_call.name
        args = tool_call.arguments
        
        if name == "get_transaction":
            result = await db.execute(select(CanonicalTransaction).where(CanonicalTransaction.id == args["transaction_id"]))
            txn = result.scalar_one_or_none()
            return {"name": name, "result": txn.__dict__ if txn else None}
        
        elif name == "get_source_records":
            from backend.app.db.models import SourceTransaction
            result = await db.execute(select(SourceTransaction).where(SourceTransaction.canonical_transaction_id == args["canonical_id"]))
            records = result.scalars().all()
            return {"name": name, "result": [r.__dict__ for r in records]}
        
        elif name == "search_similar":
            query = select(CanonicalTransaction)
            if args.get("amount"):
                query = query.where(CanonicalTransaction.amount == Decimal(str(args["amount"])))
            if args.get("counterparty"):
                query = query.where(CanonicalTransaction.counterparty.ilike(f"%{args['counterparty']}%"))
            if args.get("date_from"):
                query = query.where(CanonicalTransaction.date >= date.fromisoformat(args["date_from"]))
            if args.get("date_to"):
                query = query.where(CanonicalTransaction.date <= date.fromisoformat(args["date_to"]))
            if args.get("direction"):
                query = query.where(CanonicalTransaction.direction == args["direction"])
            result = await db.execute(query.limit(10))
            return {"name": name, "result": [r.__dict__ for r in result.scalars().all()]}
        
        elif name == "calculate_difference":
            a = args["record_a"]
            b = args["record_b"]
            diff = Decimal(str(a.get("amount", 0))) - Decimal(str(b.get("amount", 0)))
            return {"name": name, "result": {"amount_diff": str(diff), "details": f"{a.get('amount')} - {b.get('amount')} = {diff}"}}
        
        return {"name": name, "result": None, "error": "Unknown tool"}
    
    async def _validate_ai_resolution(
        self, 
        db: AsyncSession, 
        ai_resolution: AIResolution, 
        exception: Exception,
        txn: CanonicalTransaction
    ) -> tuple[bool, str]:
        """
        Validate AI resolution against business rules and actual data.
        Returns (is_valid, error_message).
        """
        # 1. Pydantic validation already done via AIResolution(**ai_output)
        
        # 2. Confidence threshold check
        if ai_resolution.confidence < self.config.confidence_auto_resolve:
            return False, f"Confidence {ai_resolution.confidence:.2f} below auto-resolve threshold {self.config.confidence_auto_resolve}"
        
        # 2. Business rule: classification must match exception type or be valid
        valid_classifications = [
            ExceptionType.AMOUNT_MISMATCH,
            ExceptionType.DATE_MISMATCH,
            ExceptionType.MISSING_RECORD,
            ExceptionType.DUPLICATE,
            ExceptionType.CURRENCY_MISMATCH,
            ExceptionType.UNKNOWN_TRANSACTION,
            ExceptionType.PROCESSOR_FEE,
            ExceptionType.AMBIGUOUS_MATCH,
            ExceptionType.REFERENCE_MISMATCH,
        ]
        if ai_resolution.classification not in valid_classifications:
            return False, f"Invalid classification: {ai_resolution.classification}"
        
        # 3. Business rule: status must be valid
        if ai_resolution.status not in [ResolutionStatus.RESOLVED, ResolutionStatus.ESCALATED, ResolutionStatus.UNRESOLVED]:
            return False, f"Invalid status: {ai_resolution.status}"
        
        # 4. Business rule: evidence must be provided for resolved/escalated
        if ai_resolution.status in [ResolutionStatus.RESOLVED, ResolutionStatus.ESCALATED] and not ai_resolution.evidence:
            return False, "Evidence required for resolved/escalated status"
        
        # 5. Business rule: explanation must not be empty
        if not ai_resolution.explanation or len(ai_resolution.explanation.strip()) < 10:
            return False, "Explanation must be at least 10 characters"
        
        # 6. Business rule verification: verify evidence against actual data
        # If classification is processor_fee, verify processor record exists
        if ai_resolution.classification == ExceptionType.PROCESSOR_FEE:
            if not await self._verify_processor_fee(db, exception):
                return False, "Processor fee classification not supported by data"
        
        # 6b. Date mismatch verification
        if ai_resolution.classification == ExceptionType.DATE_MISMATCH:
            if not await self._verify_date_mismatch(db, exception):
                return False, "Date mismatch classification not supported by data"
        
        # 6c. Amount mismatch verification
        if ai_resolution.classification == ExceptionType.AMOUNT_MISMATCH:
            if not await self._verify_amount_mismatch(db, exception):
                return False, "Amount mismatch classification not supported by data"
        
        # 6c. Processor fee verification
        if ai_resolution.classification == ExceptionType.PROCESSOR_FEE:
            if not await self._verify_processor_fee(db, exception):
                return False, "Processor fee classification not supported by data"
        
        # 6d. Duplicate verification
        if ai_resolution.classification == ExceptionType.DUPLICATE:
            if not await self._verify_duplicate(db, exception):
                return False, "Duplicate classification not supported by data"
        
        # 7. Confidence must be reasonable for the classification
        min_confidence = {
            ExceptionType.PROCESSOR_FEE: 0.85,
            ExceptionType.DATE_MISMATCH: 0.80,
            ExceptionType.AMOUNT_MISMATCH: 0.80,
            ExceptionType.ROUNDING_DIFFERENCE: 0.90,
            ExceptionType.REFERENCE_MISMATCH: 0.75,
            ExceptionType.DUPLICATE: 0.85,
            ExceptionType.MISSING_RECORD: 0.70,
            ExceptionType.AMBIGUOUS_MATCH: 0.50,
            ExceptionType.UNKNOWN_TRANSACTION: 0.50,
            ExceptionType.REFERENCE_MISMATCH: 0.75,
            ExceptionType.CURRENCY_MISMATCH: 0.80,
        }
        min_conf = min_confidence.get(ai_resolution.classification, 0.50)
        if ai_resolution.confidence < min_conf:
            return False, f"Confidence {ai_resolution.confidence:.2f} below minimum {min_conf} for {ai_resolution.classification}"
        
        # 8. Evidence must be specific and cite actual data
        for evidence in ai_resolution.evidence:
            if len(evidence.strip()) < 5:
                return False, "Evidence items must be specific and substantive"
        
        return True, ""
    
    async def _verify_processor_fee(self, db: AsyncSession, exception: Exception) -> bool:
        """Verify that a processor fee explanation is supported by actual data."""
        txn_result = await db.execute(
            select(CanonicalTransaction).where(CanonicalTransaction.id == exception.transaction_id)
        )
        txn = txn_result.scalar_one_or_none()
        if not txn:
            return False
        
        # Search for processor record that matches the ledger/bank pair
        # Look for processor with same counterparty, similar date, and amount close to ledger amount
        ledger_amount = txn.amount
        
        from backend.app.db.models import TransactionSource
        for txn in transactions:
            if txn.source != TransactionSource.PROCESSOR:
                continue
            if txn.counterparty != ledger_txn.counterparty:
                continue
            # Check if processor amount matches ledger amount (gross amount)
            if abs(txn.amount - ledger_txn.amount) <= Decimal("1.00"):
                # Found matching processor record, extract fee from metadata
                fee_str = txn.txn_metadata.get("processor_fee")
                if fee_str is not None:
                    try:
                        return Decimal(fee_str)
                    except:
                        pass
        return None
    
    async def _verify_date_mismatch(self, db: AsyncSession, exception: Exception) -> bool:
        """Verify that a date mismatch explanation is supported by data."""
        txn_result = await db.execute(
            select(CanonicalTransaction).where(CanonicalTransaction.id == exception.transaction_id)
        )
        txn = txn_result.scalar_one_or_none()
        if not txn:
            return False
        
        # Check if there are matching transactions with same amount and counterparty but different dates
        from backend.app.db.models import TransactionSource
        result = await db.execute(
            select(CanonicalTransaction).where(
                CanonicalTransaction.counterparty == txn.counterparty,
                CanonicalTransaction.amount == txn.amount,
                CanonicalTransaction.source != txn.source,
                CanonicalTransaction.date != txn.date
            )
        )
        other_txns = result.scalars().all()
        return len(other_txns) > 0
    
    async def _verify_amount_mismatch(self, db: AsyncSession, exception: Exception) -> bool:
        """Verify that an amount mismatch explanation is supported by data."""
        txn_result = await db.execute(
            select(CanonicalTransaction).where(CanonicalTransaction.id == exception.transaction_id)
        )
        txn = txn_result.scalar_one_or_none()
        if not txn:
            return False
        
        # Check if there are matching transactions with same counterparty/date but different amounts
        from backend.app.db.models import TransactionSource
        result = await db.execute(
            select(CanonicalTransaction).where(
                CanonicalTransaction.counterparty == txn.counterparty,
                CanonicalTransaction.date == txn.date,
                CanonicalTransaction.source != txn.source
            )
        )
        other_txns = result.scalars().all()
        
        if not other_txns:
            return False
        
        # Check if any other source has different amount
        for other in other_txns:
            if other.amount != txn.amount:
                return True
        return False
    
    async def _verify_duplicate(self, db: AsyncSession, exception: Exception) -> bool:
        """Verify that a duplicate explanation is supported by data."""
        txn_result = await db.execute(
            select(CanonicalTransaction).where(CanonicalTransaction.id == exception.transaction_id)
        )
        txn = txn_result.scalar_one_or_none()
        if not txn:
            return False
        
        # Check for duplicate transactions (same source, counterparty, amount, date)
        from backend.app.db.models import TransactionSource
        result = await db.execute(
            select(CanonicalTransaction).where(
                CanonicalTransaction.source == txn.source,
                CanonicalTransaction.counterparty == txn.counterparty,
                CanonicalTransaction.amount == txn.amount,
                CanonicalTransaction.date == txn.date,
                CanonicalTransaction.id != txn.id
            )
        )
        duplicates = result.scalars().all()
        return len(duplicates) > 0
    
    async def _log_audit(self, db: AsyncSession, action: AuditAction, entity_id: int, reason: str):
        log = AuditLog(actor="ai_investigator", entity="exception", entity_id=entity_id, action=action, reason=reason)
        db.add(log)
        await db.commit()

    async def close(self):
        await self.provider.close()