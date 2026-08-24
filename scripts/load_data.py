import polars as pl
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from backend.app.db.models import SourceTransaction, TransactionSource, TransactionDirection, Base
from datetime import date, datetime
from decimal import Decimal
import asyncio
import os
from pathlib import Path

# Load .env
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())

DB_PASSWORD = os.getenv("DB_PASSWORD", "finance_pass")
DATABASE_URL = f"postgresql+asyncpg://finance_user:{DB_PASSWORD}@localhost:5432/ai_finance"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def parse_date(val):
    if isinstance(val, date):
        return val
    if isinstance(val, str):
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(val, fmt).date()
            except ValueError:
                continue
    return date.today()


async def load_csv_data():
    async with async_session() as db:
        bank_df = pl.read_csv("data/bank.csv")
        ledger_df = pl.read_csv("data/ledger.csv")
        processor_df = pl.read_csv("data/processor.csv")

        for row in bank_df.iter_rows(named=True):
            txn = SourceTransaction(
                source=TransactionSource.BANK,
                source_id=str(row["id"]),
                transaction_date=parse_date(row["transaction_date"]),
                amount=Decimal(str(row["amount"])),
                currency=row["currency"],
                counterparty=row["counterparty"],
                description=row["description"],
                reference=row["bank_reference"],
                direction=TransactionDirection(row["direction"]),
                raw_data={
                    "dr_cr": row["dr_cr"],
                    "original_id": row["id"],
                }
            )
            db.add(txn)

        for row in ledger_df.iter_rows(named=True):
            txn = SourceTransaction(
                source=TransactionSource.LEDGER,
                source_id=str(row["invoice_id"]),  # Use invoice_id as unique source_id for ledger
                transaction_date=parse_date(row["transaction_date"]),
                amount=Decimal(str(row["amount"])),
                currency=row["currency"],
                counterparty=row["counterparty"],
                description=row["description"],
                reference=row["invoice_id"],
                direction=TransactionDirection(row["direction"]),
                raw_data={
                    "invoice_id": row["invoice_id"],
                    "account": row["account"],
                    "status": row["status"],
                    "original_id": row["id"],
                }
            )
            db.add(txn)

        for row in processor_df.iter_rows(named=True):
            txn = SourceTransaction(
                source=TransactionSource.PROCESSOR,
                source_id=str(row["id"]),
                transaction_date=parse_date(row["transaction_date"]),
                amount=Decimal(str(row["gross_amount"])),
                currency=row["currency"],
                counterparty=row["counterparty"],
                description=row["description"],
                reference=row["processor_reference"],
                direction=TransactionDirection.INFLOW,
                raw_data={
                    "gross_amount": str(row["gross_amount"]),
                    "fee": str(row["fee"]),
                    "net_amount": str(row["net_amount"]),
                    "processor_reference": row["processor_reference"],
                    "settlement_date": str(row["settlement_date"]),
                    "original_id": row["id"],
                }
            )
            db.add(txn)

        await db.commit()
        print(f"Loaded: {len(bank_df)} bank, {len(ledger_df)} ledger, {len(processor_df)} processor transactions")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(load_csv_data())