from decimal import Decimal
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.db.models import (
    CanonicalTransaction, Match, MatchStatus, Exception, ExceptionStatus,
    Resolution, ResolutionStatus, CashPosition
)
from backend.app.schemas.canonical import MetricsResponse


class EvaluationEngine:
    def __init__(self):
        pass

    async def compute_all(self, db: AsyncSession) -> MetricsResponse:
        total_result = await db.execute(select(CanonicalTransaction))
        total_records = len(total_result.scalars().all())

        match_result = await db.execute(select(Match))
        matches = match_result.scalars().all()
        matched_records = len([m for m in matches if m.status == MatchStatus.MATCHED])
        probable_records = len([m for m in matches if m.status == MatchStatus.PROBABLE_MATCH])

        exc_result = await db.execute(select(Exception))
        exceptions = exc_result.scalars().all()
        exceptions_total = len(exceptions)

        resolved_exceptions = len([e for e in exceptions if e.status == ExceptionStatus.RESOLVED])
        escalated_exceptions = len([e for e in exceptions if e.status == ExceptionStatus.ESCALATED])
        unresolved_exceptions = len([e for e in exceptions if e.status == ExceptionStatus.UNRESOLVED])

        match_rate = (matched_records / total_records * 100) if total_records > 0 else 0

        pos_result = await db.execute(select(CashPosition).order_by(CashPosition.date.desc()).limit(1))
        position = pos_result.scalar_one_or_none()
        cash_variance = position.variance if position else Decimal("0")

        return MetricsResponse(
            total_records=total_records,
            matched_records=matched_records,
            match_rate=match_rate,
            accuracy=0.0,
            false_match_rate=0.0,
            exceptions_total=exceptions_total,
            exceptions_resolved=resolved_exceptions,
            exceptions_escalated=escalated_exceptions,
            exceptions_unresolved=unresolved_exceptions,
            processing_time_seconds=0.0,
            cash_variance=cash_variance,
        )

    async def compute_ground_truth_accuracy(self, db: AsyncSession, ground_truth_path: str) -> Dict[str, Any]:
        import polars as pl
        gt = pl.read_parquet(ground_truth_path)
        
        match_result = await db.execute(select(Match))
        matches = match_result.scalars().all()
        
        correct = 0
        total_decisions = 0
        false_matches = 0
        
        for match in matches:
            total_decisions += 1
            gt_row = gt.filter(
                (pl.col("source_id") == match.canonical_transaction_id) |
                (pl.col("matched_source_id") == match.matched_transaction_id)
            )
            if len(gt_row) > 0:
                if gt_row[0]["ground_truth"] == "match":
                    correct += 1
                else:
                    false_matches += 1
        
        accuracy = (correct / total_decisions * 100) if total_decisions > 0 else 0
        false_match_rate = (false_matches / total_decisions * 100) if total_decisions > 0 else 0
        
        return {
            "accuracy": accuracy,
            "false_match_rate": false_match_rate,
            "correct_decisions": correct,
            "total_decisions": total_decisions,
        }