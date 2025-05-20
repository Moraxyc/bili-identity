from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, String

from .Base import Base


class User(Base):
    __tablename__ = "users"

    uid = Column(String, primary_key=True, index=True, comment="B站UID")
    nickname = Column(String, nullable=True, comment="昵称，可能会变")
    is_verified = Column(Boolean, default=False, comment="是否已通过验证")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
