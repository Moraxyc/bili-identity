from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from .Base import Base


class Token(Base):
    __tablename__ = "tokens"

    code: Mapped[str] = mapped_column(String, primary_key=True)
    uid: Mapped[str] = mapped_column(String, ForeignKey("users.uid"))
    client_id: Mapped[str] = mapped_column(
        String, ForeignKey("clients.client_id")
    )
    access_token: Mapped[str] = mapped_column(String, nullable=False)
    id_token: Mapped[str | None] = mapped_column(String, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
