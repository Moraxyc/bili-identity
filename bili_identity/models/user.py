from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, String

from .Base import Base


class User(Base):
    __tablename__ = "users"

    uid = Column(String, primary_key=True, index=True, comment="B站UID")
    nickname = Column(String, nullable=True, comment="昵称, 无法实时更新")
    avatar_url = Column(
        String,
        nullable=True,
        comment="用户头像的链接，B站应该不会让其失效",
    )
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
