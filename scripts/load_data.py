import polars as pl
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.db.models import SourceTransaction, TransactionSource, TransactionDirection
from backend.app.db.session import get_db
from datetime import date
from decimal import Decimal
import asyncio


async def load_csv_data():
    async for db in get_db():
        bank_df = pl.read_csv("data/bank.csv")
        ledger_df = pl.read_csv("data/ledger.csv")
        processor_df = pl.read_csv("data/processor.csv")
        
        for row in bank_df.iter_rows(named=True):
            txn = SourceTransaction(
                source=TransactionSource.BANK,
                source_id=str(row["id"]),
                transaction_date=row["transaction_date"],
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
                source_id=str(row["id"]),
                transaction_date=row["transaction_date"],
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
                transaction_date=row["transaction_date"],
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


if __name__ == "__main__":
    asyncio.run(load_csv_data())