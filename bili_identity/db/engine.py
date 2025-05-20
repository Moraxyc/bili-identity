from sqlalchemy.ext.asyncio import create_async_engine

from bili_identity.config import get_config


def get_async_engine():
    config = get_config()
    return create_async_engine(
        config.database.uri,
        echo=config.log.level == "DEBUG",
        pool_pre_ping=True,
        future=True,
    )
