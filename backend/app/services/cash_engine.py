from decimal import Decimal
from datetime import date, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from backend.app.db.models import (
    CanonicalTransaction, Match, MatchStatus, Exception, 
    CashPosition, ForecastEntry, TransactionDirection, TransactionSource
)
from backend.app.config import get_settings


class CashEngine:
    def __init__(self, opening_balance: int):
        self.opening_balance = Decimal(str(opening_balance))

    async def calculate_position(
        self, 
        db: AsyncSession, 
        as_of_date: date = None,
        opening_balance: Optional[Decimal] = None,
        manual_bank_cash: Optional[Decimal] = None,
        adjustments: Optional[Decimal] = None,
        adjustment_note: Optional[str] = None
    ) -> CashPosition:
        """
        Calculate cash position as of a given date.
        
        Args:
            db: Database session
            as_of_date: Date to calculate position for (default: today)
            opening_balance: Override opening balance (default: config value)
            manual_bank_cash: Override bank cash (if known from external source)
            adjustments: Manual adjustments to apply
            adjustment_note: Description of adjustments
            
        Returns:
            CashPosition object (not yet committed to DB)
        """
        if as_of_date is None:
            as_of_date = date.today()
        
        if opening_balance is not None:
            opening_balance = Decimal(str(opening_balance))
        else:
            opening_balance = self.opening_balance
        
        if adjustments is None:
            adjustments = Decimal("0")
        
        # Get confirmed matches (MATCHED status only)
        matched_result = await db.execute(
            select(CanonicalTransaction, Match)
            .join(Match, CanonicalTransaction.id == Match.canonical_transaction_id)
            .where(Match.status == MatchStatus.MATCHED)
        )
        matched = matched_result.all()
        
        confirmed_inflows = Decimal("0")
        confirmed_outflows = Decimal("0")
        
        for txn, match in matched:
            if txn.direction == TransactionDirection.INFLOW:
                confirmed_inflows += txn.amount
            else:
                confirmed_outflows += txn.amount
        
        # Get pending items (probable matches + exceptions) - only those as of as_of_date
        probable_result = await db.execute(
            select(CanonicalTransaction, Match)
            .join(Match, CanonicalTransaction.id == Match.canonical_transaction_id)
            .where(Match.status == MatchStatus.PROBABLE_MATCH)
        )
        probable = probable_result.all()
        
        pending_inflows = Decimal("0")
        pending_outflows = Decimal("0")
        
        for txn, match in probable:
            if txn.direction == TransactionDirection.INFLOW:
                pending_inflows += txn.amount
            else:
                pending_outflows += txn.amount
        
        # Exceptions - only those as of as_of_date
        exc_result = await db.execute(
            select(Exception)
            .where(Exception.created_at <= as_of_date)
        )
        exceptions = exc_result.scalars().all()
        
        pending_inflows_total = Decimal("0")
        pending_outflows_total = Decimal("0")
        
        for exc in exceptions:
            txn_result = await db.execute(
                select(CanonicalTransaction).where(CanonicalTransaction.id == exc.transaction_id)
            )
            txn = txn_result.scalar_one_or_none()
            if txn:
                if txn.direction == TransactionDirection.INFLOW:
                    pending_inflows_total += txn.amount
                else:
                    pending_outflows_total += txn.amount
        
        pending_inflows += pending_inflows_total
        pending_outflows += pending_outflows_total
        
        # Calculate bank cash from bank transactions (source=BANK) up to as_of_date
        bank_result = await db.execute(
            select(CanonicalTransaction)
            .where(
                CanonicalTransaction.source == TransactionSource.BANK,
                CanonicalTransaction.date <= as_of_date
            )
        )
        bank_transactions = bank_result.scalars().all()
        
        bank_inflows = Decimal("0")
        bank_outflows = Decimal("0")
        for txn in bank_transactions:
            if txn.direction == TransactionDirection.INFLOW:
                bank_inflows += txn.amount
            else:
                bank_outflows += txn.amount
        
        bank_cash_calculated = bank_inflows - bank_outflows
        
        # Use manual bank cash if provided, otherwise calculated
        bank_cash = manual_bank_cash if manual_bank_cash is not None else bank_cash_calculated
        
        # Apply adjustments
        adjustments = adjustments if adjustments is not None else Decimal("0")
        
        # Re-query confirmed inflows/outflows (needed after refactor)
        matched_result = await db.execute(
            select(CanonicalTransaction, Match)
            .join(Match, CanonicalTransaction.id == Match.canonical_transaction_id)
            .where(Match.status == MatchStatus.MATCHED)
        )
        matched = matched_result.all()
        
        confirmed_inflows = Decimal("0")
        confirmed_outflows = Decimal("0")
        
        for txn, match in matched:
            if txn.direction == TransactionDirection.INFLOW:
                confirmed_inflows += txn.amount
            else:
                confirmed_outflows += txn.amount
        
        # Calculate expected cash
        expected_cash = opening_balance + confirmed_inflows - confirmed_outflows + adjustments
        bank_cash_final = manual_bank_cash if manual_bank_cash is not None else bank_cash_calculated
        variance = bank_cash_final - (opening_balance + confirmed_inflows - confirmed_outflows + adjustments)
        
        # Variance breakdown
        variance_breakdown = await self._calculate_variance_breakdown(
            db, as_of_date, confirmed_inflows, confirmed_outflows, 
            pending_inflows, pending_outflows, adjustments, bank_cash_final
        )
        
        position = CashPosition(
            date=as_of_date,
            opening_balance=opening_balance,
            confirmed_inflows=confirmed_inflows,
            confirmed_outflows=confirmed_outflows,
            pending_inflows=pending_inflows,
            pending_outflows=pending_outflows,
            adjustments=adjustments,
            expected_cash=expected_cash,
            bank_cash=bank_cash_final,
            variance=variance,
        )
        
        return position

    async def _calculate_variance_breakdown(
        self,
        db: AsyncSession,
        as_of_date: date,
        confirmed_inflows: Decimal,
        confirmed_outflows: Decimal,
        pending_inflows: Decimal,
        pending_outflows: Decimal,
        adjustments: Decimal,
        bank_cash: Decimal,
    ) -> Dict[str, Decimal]:
        """Calculate detailed variance breakdown."""
        # Expected cash position
        opening_balance = self.opening_balance
        expected_cash = opening_balance + confirmed_inflows - confirmed_outflows
        
        # Variance components
        variance_due_to_pending = pending_inflows - pending_outflows
        variance_due_to_adjustments = adjustments if adjustments else Decimal("0")
        
        # Bank cash variance (difference between expected and actual bank cash)
        bank_cash_variance = bank_cash - (bank_cash)  # This would be 0 if bank_cash is calculated
        
        # Exception-based variance
        exc_result = await db.execute(
            select(Exception).where(Exception.created_at <= date.today())
        )
        exceptions = exc_result.scalars().all()
        
        exception_variance = Decimal("0")
        for exc in exceptions:
            txn_result = await db.execute(
                select(CanonicalTransaction).where(CanonicalTransaction.id == exc.transaction_id)
            )
            txn = txn_result.scalar_one_or_none()
            if txn:
                exception_variance += txn.amount if txn.direction == TransactionDirection.INFLOW else -txn.amount
        
        return {
            "total_variance": bank_cash - (bank_cash),  # Will be calculated properly
            "pending_inflows": Decimal("0"),
            "pending_outflows": Decimal("0"),
            "adjustments": adjustments,
            "exception_variance": exception_variance,
            "bank_cash_variance": Decimal("0"),
        }

    async def generate_forecast(self, db: AsyncSession, horizons: List[int] = None) -> List[ForecastEntry]:
        if horizons is None:
            horizons = [7, 14, 30]
        
        settings = get_settings()
        entries = []
        base_date = date.today()
        
        for event in settings.forecast.scheduled_events:
            event_date = base_date
            try:
                event_date = date.fromisoformat(event.next_date)
            except:
                pass
            
            # Handle recurring events
            event_dates = self._expand_recurring_event(event, base_date, max(horizons))
            
            for event_date in event_dates:
                for horizon in horizons:
                    if (event_date - date.today()).days <= horizon:
                        entry = ForecastEntry(
                            forecast_date=event_date,
                            horizon_days=horizon,
                            event_name=event.name,
                            amount=Decimal(str(event.amount)),
                            frequency=event.frequency,
                            is_recurring=True,
                        )
                        db.add(entry)
        
        await db.commit()
        result = await db.execute(select(ForecastEntry))
        return result.scalars().all()

    def _expand_recurring_event(self, event: Any, base_date: date, max_days: int) -> List[date]:
        """Expand a recurring event into multiple dates within the horizon."""
        dates = []
        event_date = date.fromisoformat(event.next_date)
        frequency = event.frequency.lower()
        
        current = event_date
        max_date = date.today() + timedelta(days=max_days)
        
        while current <= max_date:
            if current >= date.today():
                dates.append(current)
            # Move to next occurrence
            if frequency == "daily":
                current += timedelta(days=1)
            elif frequency == "weekly":
                current += timedelta(weeks=1)
            elif frequency == "monthly":
                # Add one month (approximate)
                if current.month == 12:
                    current = current.replace(year=current.year + 1, month=1)
                else:
                    current = current.replace(month=current.month + 1)
            elif frequency == "quarterly":
                # Add 3 months
                month = current.month + 3
                year = current.year
                if month > 12:
                    month -= 12
                    year += 1
                current = current.replace(year=year, month=month)
            elif frequency == "yearly":
                current = current.replace(year=current.year + 1)
            else:
                break  # Non-recurring or unknown frequency
        
        return dates

    def get_forecast_summary(self, entries: List[ForecastEntry], horizons: List[int]) -> Dict[int, Dict[str, Decimal]]:
        summary = {}
        for horizon in horizons:
            inflows = Decimal("0")
            outflows = Decimal("0")
            for entry in entries:
                if entry.horizon_days <= horizon:
                    if entry.amount > 0:
                        inflows += entry.amount
                    else:
                        outflows += abs(entry.amount)
            summary[horizon] = {
                "inflows": inflows,
                "outflows": outflows,
                "net": inflows - outflows,
            }
        return summary