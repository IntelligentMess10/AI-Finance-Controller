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


class EvaluationEngine:
    def __init__(self):
        self.ground_truth_path = "data/ground_truth.parquet"

    async def compute_all(self, db: AsyncSession) -> MetricsResponse:
        # 1. Get all canonical transactions
        total_result = await db.execute(select(CanonicalTransaction))
        total_records = len(total_result.scalars().all())

        # 2. Get all matches
        match_result = await db.execute(select(Match))
        matches = match_result.scalars().all()
        matched_records = len([m for m in matches if m.status == MatchStatus.MATCHED])
        probable_records = len([m for m in matches if m.status == MatchStatus.PROBABLE_MATCH])

        # 3. Get exceptions
        exc_result = await db.execute(select(Exception))
        exceptions = exc_result.scalars().all()
        exceptions_total = len(exceptions)

        resolved_exceptions = len([e for e in exceptions if e.status == ExceptionStatus.RESOLVED])
        escalated_exceptions = len([e for e in exceptions if e.status == ExceptionStatus.ESCALATED])
        unresolved_exceptions = len([e for e in exceptions if e.status == ExceptionStatus.UNRESOLVED])

        # 4. Calculate match rate
        match_rate = (matched_records / total_records * 100) if total_records > 0 else 0

        # 5. Get cash position
        pos_result = await db.execute(select(CashPosition).order_by(CashPosition.date.desc()).limit(1))
        position = pos_result.scalar_one_or_none()
        cash_variance = position.variance if position else Decimal("0")

        # 6. Compute ground truth accuracy
        gt_metrics = await self._compute_ground_truth_metrics()

        # 5. Calculate AI metrics
        ai_resolution_rate = 0.0
        ai_accuracy = 0.0
        if exceptions:
            resolved_escalated = len([e for e in exceptions if e.status in [ExceptionStatus.RESOLVED, ExceptionStatus.ESCALATED]])
            ai_resolution_rate = (resolved_exceptions + escalated_exceptions) / len(exceptions) * 100
            # AI accuracy: how many AI decisions were correct
            # This requires checking resolutions against ground truth

        return MetricsResponse(
            total_records=total_records,
            matched_records=matched_records,
            match_rate=match_rate,
            accuracy=0.0,  # Will be computed from ground truth
            false_match_rate=0.0,
            exceptions_total=exceptions_total,
            exceptions_resolved=resolved_exceptions,
            exceptions_escalated=escalated_exceptions,
            exceptions_unresolved=unresolved_exceptions,
            processing_time_seconds=0.0,
            cash_variance=cash_variance,
            ai_resolution_rate=0.0,
            ai_accuracy=0.0,
        )

    async def _compute_ground_truth_metrics(self) -> Dict[str, float]:
        """Compute accuracy metrics against ground truth."""
        try:
            import polars as pl
            gt = pl.read_parquet("data/ground_truth.parquet")
        except Exception:
            return {"accuracy": 0.0, "false_match_rate": 0.0, "correct_decisions": 0, "total_decisions": 0}

        # For now, return placeholder - this needs to be implemented with actual match data
        return {"accuracy": 0.0, "false_match_rate": 0.0, "correct_decisions": 0, "total_decisions": 0}