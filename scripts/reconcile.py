import asyncio
import os
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func
from backend.app.db.models import SourceTransaction, CanonicalTransaction, Match, Exception
from backend.app.services.matching import ReconciliationEngine
from backend.app.config import get_settings
from backend.app.db.session import Base
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

logger = logging.getLogger(__name__)

DB_PASSWORD = os.getenv("DB_PASSWORD", "finance_pass")
DATABASE_URL = f"postgresql+asyncpg://finance_user:{DB_PASSWORD}@localhost:5432/ai_finance"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def run_reconciliation():
    settings = get_settings()
    async with async_session() as db:
        # Clear previous reconciliation results
        from sqlalchemy import text
        await db.execute(text("TRUNCATE matches, exceptions RESTART IDENTITY CASCADE"))
        await db.commit()
        
        # Get canonical transactions
        result = await db.execute(select(CanonicalTransaction))
        transactions = result.scalars().all()
        
        logger.info(f"Running reconciliation on {len(transactions)} canonical transactions...")
        
        # Run reconciliation
        recon_engine = ReconciliationEngine(settings.matching)
        result = await recon_engine.run(db, transactions)
        
        # Print stats
        stats = result["stats"]
        print(f"\n=== Reconciliation Results ===")
        print(f"Total transactions: {stats['total']}")
        print(f"Matched: {stats['matched']}")
        print(f"Probable matches: {stats['probable']}")
        print(f"Exceptions: {stats['exceptions']}")
        print(f"Match rate: {stats['matched'] / stats['total'] * 100:.1f}%")
        
        # Verify DB state
        total_matches = await db.scalar(select(func.count(Match.id)))
        total_exceptions = await db.scalar(select(func.count(Exception.id)))
        print(f"\nDB verification:")
        print(f"  Matches in DB: {total_matches}")
        print(f"  Exceptions in DB: {total_exceptions}")
        
        # Sample some matches
        sample = await db.execute(select(Match).limit(5))
        for m in sample.scalars().all():
            txn1 = await db.get(CanonicalTransaction, m.canonical_transaction_id)
            txn2 = await db.get(CanonicalTransaction, m.matched_transaction_id)
            print(f"\n  Match #{m.id}: {txn1.counterparty} ({txn1.amount}) <-> {txn2.counterparty} ({txn2.amount})")
            print(f"    Score: {m.score:.3f} | Method: {m.method} | Status: {m.status}")
            print(f"    Evidence: {m.evidence}")

        # Sample exceptions
        exc_sample = await db.execute(select(Exception).limit(5))
        for e in exc_sample.scalars().all():
            txn = await db.get(CanonicalTransaction, e.transaction_id)
            print(f"\n  Exception #{e.id}: {txn.counterparty} ({txn.amount})")
            print(f"    Type: {e.type} | Status: {e.status} | Severity: {e.severity}")
            print(f"    Description: {e.description}")
            print(f"    Evidence: {e.evidence}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(run_reconciliation())