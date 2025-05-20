from fastapi import APIRouter, HTTPException
from schemas.auth import SubmitUIDRequest, VerifyCodeRequest
from services import send_code, verify_code

router = APIRouter(prefix="/api/auth")


@router.post("/send")
async def request_code(data: SubmitUIDRequest):
    await send_code(data.uid)
    return {"message": "验证码已发送"}


@router.post("/verify")
async def submit_code(data: VerifyCodeRequest):
    is_valid = await verify_code(data.uid, data.code)
    if is_valid:
        return {"message": "验证成功"}
    raise HTTPException(status_code=400, detail="验证码错误或已过期")
