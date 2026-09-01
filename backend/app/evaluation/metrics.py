from decimal import Decimal
from typing import Dict, Any, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.app.db.models import (
    CanonicalTransaction, Match, MatchStatus, Exception, ExceptionStatus,
    Resolution, ResolutionStatus, CashPosition
)
from backend.app.schemas.canonical import MetricsResponse
import polars as pl
import time


class EvaluationEngine:
    def __init__(self):
        self.ground_truth_path = "data/ground_truth.parquet"

    async def compute_all(self, db: AsyncSession, processing_time: float = 0.0) -> MetricsResponse:
        # 1. Get all canonical transactions
        total_result = await db.execute(select(CanonicalTransaction))
        total_records = len(total_result.scalars().all())

        # 2. Get all matches
        match_result = await db.execute(select(Match))
        matches = match_result.scalars().all()
        matched_txn_ids = set()
        for m in matches:
            if m.status == MatchStatus.MATCHED:
                matched_txn_ids.add(m.canonical_transaction_id)
                matched_txn_ids.add(m.matched_transaction_id)
        matched_records = len(matched_txn_ids)
        probable_records = len([m for m in matches if m.status == MatchStatus.PROBABLE_MATCH])

        # 3. Get exceptions
        exc_result = await db.execute(select(Exception))
        exceptions = exc_result.scalars().all()
        exceptions_total = len(exceptions)

        resolved_exceptions = len([e for e in exceptions if e.status == ExceptionStatus.RESOLVED])
        escalated_exceptions = len([e for e in exceptions if e.status == ExceptionStatus.ESCALATED])
        # Count OPEN and INVESTIGATING as unresolved (not yet resolved/escalated)
        unresolved_exceptions = len([e for e in exceptions if e.status in [ExceptionStatus.UNRESOLVED, ExceptionStatus.OPEN, ExceptionStatus.INVESTIGATING]])

        # 4. Calculate match rate
        match_rate = (matched_records / total_records * 100) if total_records > 0 else 0

        # 5. Get cash position
        pos_result = await db.execute(select(CashPosition).order_by(CashPosition.date.desc()).limit(1))
        position = pos_result.scalar_one_or_none()
        cash_variance = position.variance if position else Decimal("0")

        # 6. Compute ground truth accuracy
        gt_metrics = await self._compute_ground_truth_metrics(db)

        # 7. Calculate AI metrics
        ai_resolution_rate = 0.0
        ai_accuracy = 0.0
        if exceptions:
            resolved_escalated = len([e for e in exceptions if e.status in [ExceptionStatus.RESOLVED, ExceptionStatus.ESCALATED]])
            ai_resolution_rate = (resolved_exceptions + escalated_exceptions) / len(exceptions) * 100

        return MetricsResponse(
            total_records=total_records,
            matched_records=matched_records,
            match_rate=match_rate,
            accuracy=gt_metrics.get("accuracy", 0.0),
            false_match_rate=gt_metrics.get("false_match_rate", 0.0),
            exceptions_total=exceptions_total,
            exceptions_resolved=resolved_exceptions,
            exceptions_escalated=escalated_exceptions,
            exceptions_unresolved=unresolved_exceptions,
            processing_time_seconds=processing_time,
            cash_variance=cash_variance,
            ai_resolution_rate=ai_resolution_rate,
            ai_accuracy=gt_metrics.get("ai_accuracy", 0.0),
        )

    async def _compute_ground_truth_metrics(self, db: AsyncSession) -> Dict[str, float]:
        try:
            gt = pl.read_parquet(self.ground_truth_path)
        except Exception:
            return {"accuracy": 0.0, "false_match_rate": 0.0, "ai_accuracy": 0.0}

        # Get all matches with transaction details
        match_result = await db.execute(select(Match))
        matches = match_result.scalars().all()

        if not matches:
            return {"accuracy": 0.0, "false_match_rate": 0.0, "ai_accuracy": 0.0}

        # Build transaction lookup
        txn_result = await db.execute(select(CanonicalTransaction))
        txns = {t.id: t for t in txn_result.scalars().all()}

        # Get resolutions for AI accuracy
        res_result = await db.execute(select(Resolution))
        resolutions = {r.exception_id: r for r in res_result.scalars().all()}

        # Get exceptions
        exc_result = await db.execute(select(Exception))
        exceptions = {e.id: e for e in exc_result.scalars().all()}

        # Ground truth mapping: transaction_id -> ground_truth_type
        gt_map = {}
        for row in gt.iter_rows(named=True):
            # Parquet uses txn_id and ground_truth, CSV uses transaction_id and ground_truth_type
            txn_id = row.get("txn_id") or row.get("transaction_id")
            gt_type = row.get("ground_truth") or row.get("ground_truth_type")
            if txn_id and gt_type:
                gt_map[txn_id] = gt_type

        # Evaluate matches against ground truth
        total_decisions = 0
        correct_decisions = 0
        false_positives = 0
        total_matches = 0

        for m in matches:
            total_matches += 1
            txn1 = txns.get(m.canonical_transaction_id)
            txn2 = txns.get(m.matched_transaction_id)
            
            if not txn1 or not txn2:
                continue
            
            gt1 = gt_map.get(txn1.id)
            gt2 = gt_map.get(txn2.id)
            
            if gt1 and gt2:
                total_decisions += 1
                should_match = gt1 == gt2 and gt1 != "ambiguous"
                
                if m.status == MatchStatus.MATCHED:
                    if should_match:
                        correct_decisions += 1
                    else:
                        false_positives += 1
                elif m.status == MatchStatus.PROBABLE_MATCH:
                    if should_match:
                        correct_decisions += 1
                elif m.status == MatchStatus.EXCEPTION:
                    if not should_match:
                        correct_decisions += 1

        # AI accuracy: check resolutions against ground truth
        ai_correct = 0
        ai_total = 0
        for exc in exceptions.values():
            res = resolutions.get(exc.id)
            if res:
                ai_total += 1
                gt_type = gt_map.get(exc.transaction_id)
                if gt_type:
                    if res.classification.value == gt_type or \
                       (gt_type == "processor_fee" and res.classification.value == "processor_fee") or \
                       (gt_type == "amount_mismatch_fee" and res.classification.value == "amount_mismatch") or \
                       (gt_type == "amount_mismatch_rounding" and res.classification.value == "amount_mismatch") or \
                       (gt_type == "date_mismatch" and res.classification.value == "date_mismatch") or \
                       (gt_type == "missing_ledger" and res.classification.value == "missing_record") or \
                       (gt_type == "missing_bank" and res.classification.value == "missing_record") or \
                       (gt_type == "duplicate_ledger" and res.classification.value == "duplicate") or \
                       (gt_type == "reference_error" and res.classification.value == "reference_mismatch"):
                        ai_correct += 1

        accuracy = (correct_decisions / total_decisions * 100) if total_decisions > 0 else 0.0
        false_match_rate = (false_positives / total_matches * 100) if total_matches > 0 else 0.0
        ai_accuracy = (ai_correct / ai_total * 100) if ai_total > 0 else 0.0

        return {
            "accuracy": accuracy,
            "false_match_rate": false_match_rate,
            "ai_accuracy": ai_accuracy,
        }