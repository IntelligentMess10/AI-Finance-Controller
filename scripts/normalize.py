import asyncio
import os
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from backend.app.db.models import SourceTransaction, CanonicalTransaction
from backend.app.services.normalization import Normalizer
import logging

# Load .env
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

DB_PASSWORD = os.getenv("DB_PASSWORD", "finance_pass")
DATABASE_URL = f"postgresql+asyncpg://finance_user:{DB_PASSWORD}@localhost:5432/ai_finance"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def run_normalization():
    async with async_session() as db:
        normalizer = Normalizer()
        canonical_txns = await normalizer.run(db)
        
        # Verify results
        from sqlalchemy import select, func
        total_canonical = await db.scalar(select(func.count(CanonicalTransaction.id)))
        total_source = await db.scalar(select(func.count(SourceTransaction.id)))
        linked = await db.scalar(
            select(func.count(SourceTransaction.id))
            .where(SourceTransaction.canonical_transaction_id.is_not(None))
        )
        
        print(f"\n=== Normalization Results ===")
        print(f"Total source transactions: {total_source}")
        print(f"Total canonical transactions: {total_canonical}")
        print(f"Source transactions linked: {linked}")
        print(f"Unlinked source transactions: {total_source - linked}")
        
        # Sample some normalized data
        sample = await db.execute(
            select(CanonicalTransaction)
            .limit(5)
        )
        for ct in sample.scalars().all():
            print(f"\n  Canonical #{ct.id}:")
            print(f"    Source: {ct.source} | Source ID: {ct.source_id}")
            print(f"    Date: {ct.date} | Amount: {ct.amount} {ct.currency}")
            print(f"    Counterparty: {ct.counterparty}")
            print(f"    Counterparty (loose): {ct.counterparty_loose}")
            print(f"    Direction: {ct.direction}")
            print(f"    Reference: {ct.reference}")
            print(f"    Metadata keys: {list(ct.txn_metadata.keys())}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(run_normalization())