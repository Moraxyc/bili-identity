from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from .Base import Base


class User(Base):
    __tablename__ = "users"

    uid: Mapped[str] = mapped_column(
        String, primary_key=True, index=True, comment="B站UID"
    )
    nickname: Mapped[str | None] = mapped_column(
        String, nullable=True, comment="昵称, 无法实时更新"
    )
    avatar_url: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        comment="用户头像的链接，B站应该不会让其失效",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
