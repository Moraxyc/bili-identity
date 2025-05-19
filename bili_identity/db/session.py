from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from bili_identity.config import config

async_engine = create_async_engine(
    config.database.uri,
    echo=config.log.level == "DEBUG",
    pool_pre_ping=True,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
    autocommit=False,
    future=True,
)
