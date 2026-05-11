from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text
from app.core.config import settings

engine = create_async_engine(
    settings.ASYNC_DB_URL,
    echo=True,
    future=True
)

async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    """Dependency for getting async session"""
    async with async_session_maker() as session:
        yield session

async def setup_database():
    """Explicitly create the vector extension if it doesn't exist."""
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
