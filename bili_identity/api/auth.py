import logging

from fastapi import APIRouter, HTTPException

from bili_identity.schemas import SubmitUIDRequest, VerifyCodeRequest
from bili_identity.services import send_code, verify_code

auth_router = APIRouter(prefix="/api/auth")

logger = logging.getLogger(__name__)


@auth_router.post("/send")
async def request_code(data: SubmitUIDRequest):
    await send_code(data.uid)
    return {"message": "验证码已发送"}


@auth_router.post("/verify")
async def submit_code(data: VerifyCodeRequest):
    is_valid = await verify_code(data.uid, data.code)
    logger.debug(f"验证状态 {is_valid}")
    if is_valid:
        return {"message": "验证成功"}
    raise HTTPException(status_code=400, detail="验证码错误或已过期")
