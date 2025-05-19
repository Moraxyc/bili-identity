from .session import AsyncSessionLocal


async def init_db():
    async with AsyncSessionLocal() as session:
        await session.run_sync(Base.metadata.create_all)
    print("数据库初始化完成")
