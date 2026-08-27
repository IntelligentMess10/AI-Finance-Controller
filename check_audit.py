import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.models import AuditLog, AuditAction

async def check():
    engine = create_async_engine('postgresql+asyncpg://finance_user:finance_pass@localhost:5432/ai_finance')
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        from sqlalchemy import select
        from backend.app.db.models import AuditLog, AuditAction
        result = await db.execute(select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(30))
        logs = result.scalars().all()
        for log in logs:
            reason = log.reason[:80] if log.reason else ""
            print(f'{log.timestamp} | {log.action} | {log.entity} | {log.entity_id} | {reason}')
    await engine.dispose()

asyncio.run(check())