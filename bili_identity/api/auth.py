import logging

from fastapi import APIRouter, HTTPException, Request, Response

from bili_identity.config import get_config
from bili_identity.db import (
    clear_all_mappings_by_uid,
    get_status_by_session_id,
    is_session_id_exist,
    save_new_or_update_mapping,
)
from bili_identity.schemas import SubmitUIDRequest, VerifyCodeRequest
from bili_identity.services import (
    clear_all_codes_by_uid,
    gen_passive_code,
    get_token,
    is_token_valid,
    issue_tokens,
    revoke_token,
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
    session_id = save_new_or_update_mapping(data.uid)
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=True,
        max_age=config.security.code_ttl,
    )
    return {"code": code}


@auth_router.post("/send")
async def request_code(data: SubmitUIDRequest):
    """
    接收用户提交的 UID，请求发送验证码。

    :param data: 包含用户 UID 的请求数据
    :type data: SubmitUIDRequest
    :return: 返回验证码发送成功的消息
    :rtype: dict
    """
    await send_code(data.uid)
    return {"message": "验证码已发送"}


@auth_router.post("/verify")
async def submit_code(data: VerifyCodeRequest, response: Response):
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
        await set_tokens(data, response)
        return {"message": "验证成功"}
    raise HTTPException(status_code=400, detail="验证码错误或已过期")


@auth_router.post("/logout")
async def logout(request: Request, response: Response):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=400, detail="Missing refresh_token")

    claims = await get_token(token)
    if not claims:
        raise HTTPException(status_code=401, detail="Invalid token")

    if claims.get("typ") != "refresh":
        raise HTTPException(status_code=401, detail="Not a refresh token")

    jti = claims["jti"]
    await revoke_token(jti)

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"msg": "Logged out"}


@auth_router.post("/verify-passive")
async def verify_passive(
    data: SubmitUIDRequest, request: Request, response: Response
):
    """
    验证session并颁发refresh token
    """
    session_id = request.cookies["session_id"]
    if not session_id:
        raise HTTPException(status_code=401, detail="未登录")

    is_exist = is_session_id_exist(session_id)
    if not is_exist:
        raise HTTPException(status_code=400, detail="验证码错误或已过期,")

    is_valid = get_status_by_session_id(session_id)
    logger.debug(f"验证状态 {is_valid}")
    if is_valid:
        await set_tokens(data, response)
        return {"message": "验证成功"}

    raise HTTPException(status_code=202, detail="等待验证中")


@auth_router.get("/status")
async def response_is_verified(request: Request):
    """
    :return: 返回用户是否已通过验证
    :rtype: dict
    """
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="未登录")
    if not await is_token_valid(token):
        raise HTTPException(status_code=403, detail="用户尚未验证")
    return {"message": "已认证"}


async def set_tokens(
    data: SubmitUIDRequest | VerifyCodeRequest, response: Response
):
    refresh_token, access_token = await issue_tokens(data.uid, True, True)
    if access_token:
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            max_age=config.security.access_token_ttl,
            samesite="strict",
        )
    if refresh_token:
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            max_age=config.security.refresh_token_ttl,
            samesite="strict",
        )

    # 清除所有状态，只剩token
    response.delete_cookie("session_id")
    clear_all_mappings_by_uid(data.uid)
    await clear_all_codes_by_uid(data.uid)
