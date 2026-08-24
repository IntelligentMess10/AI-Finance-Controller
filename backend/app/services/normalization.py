import re
from decimal import Decimal
from datetime import date, datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.db.models import SourceTransaction, CanonicalTransaction, TransactionSource, TransactionDirection
from backend.app.config import get_settings


class Normalizer:
    def __init__(self):
        self.settings = get_settings()

    def normalize_counterparty(self, name: str) -> str:
        if not name:
            return ""
        name = name.upper().strip()
        name = re.sub(r'[^\w\s]', ' ', name)
        name = re.sub(r'\s+', ' ', name)
        suffixes = ['LTD', 'LIMITED', 'PVT', 'PRIVATE', 'INC', 'CORP', 'CORPORATION', 'LLC', 'LLP']
        words = name.split()
        words = [w for w in words if w not in suffixes]
        return ' '.join(words)

    def normalize_reference(self, ref: Optional[str]) -> Optional[str]:
        if not ref:
            return None
        ref = ref.upper().strip()
        ref = re.sub(r'[^\w\-]', '', ref)
        return ref if ref else None

    def parse_amount(self, value: Any) -> Decimal:
        if isinstance(value, Decimal):
            return value
        if isinstance(value, (int, float)):
            return Decimal(str(value))
        if isinstance(value, str):
            cleaned = re.sub(r'[^\d\.\-]', '', value)
            return Decimal(cleaned) if cleaned else Decimal("0")
        return Decimal("0")

    def parse_date(self, value: Any) -> date:
        if isinstance(value, date):
            return value
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"]:
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
        return date.today()

    def determine_direction(self, source: TransactionSource, amount: Decimal, raw: Dict) -> TransactionDirection:
        if source == TransactionSource.BANK:
            dr_cr = raw.get("dr_cr", "").upper()
            if dr_cr == "CR":
                return TransactionDirection.INFLOW
            elif dr_cr == "DR":
                return TransactionDirection.OUTFLOW
        elif source == TransactionSource.LEDGER:
            acc_type = raw.get("account_type", "").lower()
            if "receivable" in acc_type or "revenue" in acc_type or "income" in acc_type:
                return TransactionDirection.INFLOW
        elif source == TransactionSource.PROCESSOR:
            txn_type = raw.get("type", "").lower()
            if "payout" in txn_type or "refund" in txn_type:
                return TransactionDirection.OUTFLOW
            elif "payment" in txn_type or "charge" in txn_type:
                return TransactionDirection.INFLOW
        return TransactionDirection.INFLOW if amount > 0 else TransactionDirection.OUTFLOW

    def normalize_source_transaction(self, source_txn: SourceTransaction) -> CanonicalTransaction:
        amount = self.parse_amount(source_txn.amount)
        txn_date = self.parse_date(source_txn.transaction_date)
        counterparty = self.normalize_counterparty(source_txn.counterparty)
        reference = self.normalize_reference(source_txn.reference)
        direction = self.determine_direction(source_txn.source, amount, source_txn.raw_data)

        return CanonicalTransaction(
            source=source_txn.source,
            source_id=source_txn.source_id,
            date=txn_date,
            amount=amount,
            currency=source_txn.currency or "INR",
            counterparty=counterparty,
            description=source_txn.description,
            reference=reference,
            direction=direction,
            metadata={
                "raw_counterparty": source_txn.counterparty,
                "raw_reference": source_txn.reference,
                "raw_amount": str(source_txn.amount),
                "raw_date": str(source_txn.transaction_date),
            }
        )

    async def run(self, db: AsyncSession) -> List[CanonicalTransaction]:
        result = await db.execute(select(SourceTransaction).where(SourceTransaction.canonical_transaction_id.is_(None)))
        source_txns = result.scalars().all()

        canonical_txns = []
        for st in source_txns:
            canonical = self.normalize_source_transaction(st)
            db.add(canonical)
            await db.flush()
            st.canonical_transaction_id = canonical.id
            canonical_txns.append(canonical)

        await db.commit()
        return canonical_txns