from sqlalchemy.ext.asyncio import create_async_engine

from bili_identity.config import get_config

config = get_config()

async_engine = create_async_engine(
    config.database.uri,
    echo=config.log.level == "DEBUG",
    pool_pre_ping=True,
    future=True,
)
