from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from bili_identity.db.engine import get_async_engine

_async_session_factory = None


def get_session_factory() -> async_sessionmaker:
    global _async_session_factory
    if _async_session_factory is None:
        engine = get_async_engine()
        _async_session_factory = async_sessionmaker(
            bind=engine,
            autoflush=False,
            expire_on_commit=False,
            class_=AsyncSession,
            autocommit=False,
            future=True,
        )
    return _async_session_factory


class _LazySessionMaker:
    def __call__(self):
        return get_session_factory()()


AsyncSessionLocal = _LazySessionMaker()
