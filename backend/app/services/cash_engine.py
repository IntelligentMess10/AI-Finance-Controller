from decimal import Decimal
from datetime import date, timedelta
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.app.db.models import CanonicalTransaction, Match, MatchStatus, Exception, CashPosition, ForecastEntry, TransactionDirection
from backend.app.config import get_settings


class CashEngine:
    def __init__(self, opening_balance: int):
        self.opening_balance = Decimal(str(opening_balance))

    async def calculate_position(self, db: AsyncSession, as_of_date: date = None) -> CashPosition:
        if as_of_date is None:
            as_of_date = date.today()
        
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
        
        # Get pending (probable matches + exceptions)
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
        
        # Exceptions
        exc_result = await db.execute(select(Exception))
        exceptions = exc_result.scalars().all()
        
        for exc in exceptions:
            txn_result = await db.execute(select(CanonicalTransaction).where(CanonicalTransaction.id == exc.transaction_id))
            txn = txn_result.scalar_one_or_none()
            if txn:
                if txn.direction == TransactionDirection.INFLOW:
                    pending_inflows += txn.amount
                else:
                    pending_outflows += txn.amount
        
        expected_cash = self.opening_balance + confirmed_inflows - confirmed_outflows
        bank_cash = expected_cash + pending_inflows - pending_outflows  # Simplified
        variance = bank_cash - expected_cash
        
        position = CashPosition(
            date=as_of_date,
            opening_balance=self.opening_balance,
            confirmed_inflows=confirmed_inflows,
            confirmed_outflows=confirmed_outflows,
            pending_inflows=pending_inflows,
            pending_outflows=pending_outflows,
            adjustments=Decimal("0"),
            expected_cash=expected_cash,
            bank_cash=bank_cash,
            variance=variance,
        )
        
        db.add(position)
        await db.commit()
        await db.refresh(position)
        return position

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
            
            for horizon in horizons:
                if (event_date - base_date).days <= horizon:
                    entry = ForecastEntry(
                        forecast_date=event_date,
                        horizon_days=horizon,
                        event_name=event.name,
                        amount=Decimal(str(event.amount)),
                        frequency=event.frequency,
                        is_recurring=True,
                    )
                    entries.append(entry)
        
        for entry in entries:
            db.add(entry)
        await db.commit()
        
        return entries

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