from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String

from .Base import Base


class Token(Base):
    __tablename__ = "tokens"

    code = Column(String, primary_key=True)
    uid = Column(String, ForeignKey("users.uid"))
    client_id = Column(String, ForeignKey("clients.client_id"))
    access_token = Column(String, nullable=False)
    id_token = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
