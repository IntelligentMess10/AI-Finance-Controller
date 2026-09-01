#FOR TESTING PURPOSES
#SETS THE EXCEPTIONS TO OPEN AGAIN.

import asyncio
import os
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update
from backend.app.db.models import Exception, ExceptionStatus

DB_PASSWORD = os.getenv("DB_PASSWORD", "finance_pass")
DATABASE_URL = f"postgresql+asyncpg://finance_user:{DB_PASSWORD}@localhost:5432/ai_finance"

async def reset_exceptions():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        await db.execute(update(Exception).values(status=ExceptionStatus.OPEN))
        await db.commit()
        print("All exceptions reset to unresolved")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(reset_exceptions())