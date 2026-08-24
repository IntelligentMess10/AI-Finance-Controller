from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.db.models import CanonicalTransaction, Exception, Resolution, ResolutionStatus, ExceptionType, AuditLog, AuditAction
from backend.app.schemas.canonical import AIResolution
from backend.app.services.llm_providers import LLMProvider, get_provider, LLMMessage
from backend.app.config import get_settings, AIConfig


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

    async def _log_audit(self, db: AsyncSession, action: AuditAction, entity_id: int, reason: str):
        log = AuditLog(actor="ai_investigator", entity="exception", entity_id=entity_id, action=action, reason=reason)
        db.add(log)
        await db.commit()

    async def close(self):
        await self.provider.close()