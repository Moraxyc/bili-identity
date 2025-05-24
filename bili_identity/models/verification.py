from datetime import datetime, timedelta, timezone
from typing import Literal

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Enum, Integer

from .Base import Base


class VerificationCode(Base):
    __tablename__ = "verification_codes"

    uid: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, comment="B站 UID"
    )
    mode: Mapped[str] = mapped_column(
        Enum("active", "passive", name="mode_enum"),
        default="passive",
        primary_key=True,
        comment="主被动模式",
    )
    code: Mapped[str] = mapped_column(
        String, nullable=False, comment="验证码"
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, comment="过期时间"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        comment="创建时间",
    )

    def is_match(self, code: str) -> bool:
        return self.code.strip() == code.strip()

    def is_expired(self) -> bool:
        if not isinstance(self.expires_at, datetime):
            return True

        expires_at = self.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        return now > expires_at

    @classmethod
    def create(
        cls,
        uid: int,
        code: str,
        expire_minutes: int = 5,
        mode: Literal["active", "passive"] = "active",
    ):
        return cls(
            uid=uid,
            code=code.strip(),
            expires_at=datetime.now(timezone.utc)
            + timedelta(minutes=expire_minutes),
            mode=mode,
        )
