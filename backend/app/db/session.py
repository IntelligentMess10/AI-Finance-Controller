from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from backend.app.config import get_settings
from backend.app.db.base import Base
from backend.app.db import models  # noqa: F401 - registers models with Base.metadata

settings = get_settings()

DATABASE_URL = (
    f"postgresql+asyncpg://{settings.database.user}:{settings.database.password}"
    f"@{settings.database.host}:{settings.database.port}/{settings.database.name}"
)

engine = create_async_engine(DATABASE_URL, echo=settings.app.debug if hasattr(settings.app, 'debug') else False)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    await engine.dispose()