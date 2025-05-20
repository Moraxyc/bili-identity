from pydantic import BaseModel


class SubmitUIDRequest(BaseModel):
    uid: int


class VerifyCodeRequest(BaseModel):
    uid: int
    code: str
