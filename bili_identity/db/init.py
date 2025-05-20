import logging

from bili_identity.models import Base

from .engine import async_engine

logger = logging.getLogger(__name__)


async def init_db():
    logger.info("开始初始化数据库结构！")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("初始化数据库结构成功！")
