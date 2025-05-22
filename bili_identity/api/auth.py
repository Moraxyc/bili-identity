import logging

from fastapi import APIRouter, HTTPException, Request, Response

from bili_identity.config import get_config
from bili_identity.db import create_session_id
from bili_identity.schemas import SubmitUIDRequest, VerifyCodeRequest
from bili_identity.services import (
    gen_passive_code,
    is_session_verified,
    send_code,
    verify_code,
)

auth_router = APIRouter(prefix="/api/auth")

logger = logging.getLogger(__name__)

config = get_config()


@auth_router.post("/passive")
async def response_code(data: SubmitUIDRequest, response: Response):
    """
    接收用户提交的 UID，返回验证码。

    :param data: 包含用户 UID 的请求数据
    :type data: SubmitUIDRequest
    :return: 返回验证码
    :rtype: dict
    """
    code = await gen_passive_code(data.uid)
    session_id = await create_session_id(
        data.uid, config.security.session_ttl, False
    )
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=True,
        max_age=config.security.session_ttl,
    )
    return {"code": code}


@auth_router.post("/send")
async def request_code(data: SubmitUIDRequest, response: Response):
    """
    接收用户提交的 UID，请求发送验证码。

    :param data: 包含用户 UID 的请求数据
    :type data: SubmitUIDRequest
    :return: 返回验证码发送成功的消息
    :rtype: dict
    """
    await send_code(data.uid)
    session_id = await create_session_id(
        data.uid, config.security.session_ttl, False
    )
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=True,
        max_age=config.security.session_ttl,
    )
    return {"message": "验证码已发送"}


@auth_router.post("/verify")
async def submit_code(data: VerifyCodeRequest):
    """
    提交并验证验证码。

    :param data: 包含用户 ID 和验证码的请求数据
    :type data: VerifyCodeRequest
    :return: 验证成功时返回的消息字典
    :rtype: dict
    :raises HTTPException: 当验证码错误或已过期时抛出 400 异常
    """
    is_valid = await verify_code(data.uid, data.code, mode="active")
    logger.debug(f"验证状态 {is_valid}")
    if is_valid:
        return {"message": "验证成功"}
    raise HTTPException(status_code=400, detail="验证码错误或已过期")


@auth_router.get("/status")
async def response_is_verified(request: Request):
    """
    接收用户提交的 UID。

    :param data: 包含用户 UID 的请求数据
    :type data: SubmitUIDRequest
    :return: 返回用户是否已通过验证
    :rtype: dict
    """
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="未登录")
    if not await is_session_verified(session_id):
        raise HTTPException(status_code=403, detail="用户尚未验证")
    return {"message": "已认证"}
