import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from backend.app.db import models
from backend.app.db.session import Base
import os

DB_PASSWORD = os.getenv('DB_PASSWORD', 'finance_pass')
DATABASE_URL = f'postgresql+asyncpg://finance_user:{DB_PASSWORD}@localhost:5432/ai_finance'

async def check_tables():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        result = await conn.exec_driver_sql("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        tables = result.fetchall()
        print('Tables:', tables)
    await engine.dispose()

asyncio.run(check_tables())