import logging

from fastapi import APIRouter, HTTPException

from bili_identity.schemas import SubmitUIDRequest, VerifyCodeRequest
from bili_identity.services import send_code, verify_code

auth_router = APIRouter(prefix="/api/auth")

logger = logging.getLogger(__name__)


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
async def submit_code(data: VerifyCodeRequest):
    """
    提交并验证验证码。

    :param data: 包含用户 ID 和验证码的请求数据
    :type data: VerifyCodeRequest
    :return: 验证成功时返回的消息字典
    :rtype: dict
    :raises HTTPException: 当验证码错误或已过期时抛出 400 异常
    """
    is_valid = await verify_code(data.uid, data.code)
    logger.debug(f"验证状态 {is_valid}")
    if is_valid:
        return {"message": "验证成功"}
    raise HTTPException(status_code=400, detail="验证码错误或已过期")
