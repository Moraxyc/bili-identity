from datetime import datetime, timedelta, timezone
from typing import Literal

from sqlalchemy import Column, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Enum

from .Base import Base


class VerificationCode(Base):
    __tablename__ = "verification_codes"

    uid = Column(String, primary_key=True, index=True, comment="B站 UID")
    code = Column(String, nullable=False, comment="验证码")
    mode = Column(
        Enum("active", "passive", name="mode_enum"),
        default="active",
        comment="主被动模式",
    )
    expires_at = Column(DateTime(timezone=True), nullable=False, comment="过期时间")
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        comment="创建时间",
    )

    def is_expired(self) -> bool:
        if not isinstance(self.expires_at, datetime):
            return True
        now = datetime.now(timezone.utc)
        return now > self.expires_at

    @classmethod
    def create(cls, uid: str, code: str, expire_minutes: int = 5):
        return cls(
            uid=uid,
            code=code,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=expire_minutes),
        )
