from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .engine import async_engine

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
    autocommit=False,
    future=True,
)
