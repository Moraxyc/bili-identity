import logging
from contextlib import asynccontextmanager

import uvicorn
from bilibili_api.session import EventType
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from bili_identity import __version__
from bili_identity.api import (
    auth_router,
    oidc_router,
    oidc_well_known_router,
)
from bili_identity.config import MissingCredentialError, get_config

# from .api import admin, oidc
from bili_identity.db import init_db

logger = logging.getLogger(__name__)

try:
    config = get_config()
except MissingCredentialError as e:
    logger.error(f"配置错误: {e}")
    input("按 Enter 键退出...")
    raise SystemExit(1)


@asynccontextmanager
async def lifespan(_):
    logger.debug("进入初始化生命周期")
    await init_db()

    from bili_identity.core.bilibili import receive_verifiction_code

    config.session.on(EventType.TEXT)(receive_verifiction_code)

    await config.session.run()

    yield


app = FastAPI(
    title="Bili Identity",
    description="B站账号认证 OpenID Connect 兼容层",
    version=__version__,
    lifespan=lifespan,
)

# 创建app实例
# TODO: 改为配置文件里设置，以达到生产可用目的
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TODO: 完成路由
# 注册 OIDC 和管理端路由
app.include_router(auth_router)
app.include_router(oidc_router)
app.include_router(oidc_well_known_router)


@app.get("/")
def read_root():
    return {"msg": "Welcome to Bili Identity OpenID Connect Service."}


def main() -> None:
    logging.basicConfig(level=getattr(logging, config.log.level))
    uvicorn.run(
        app,
        host=config.server.host,
        port=config.server.port,
        reload=config.server.reload,
    )


if __name__ == "__main__":
    main()
