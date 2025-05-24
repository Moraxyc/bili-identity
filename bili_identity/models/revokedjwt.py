from datetime import datetime, timezone

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DateTime

from .Base import Base


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    jti: Mapped[str] = mapped_column(String(64), primary_key=True)
    revoked_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
