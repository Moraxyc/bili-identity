import json
import uuid
from datetime import datetime, timedelta, timezone

from jwcrypto import jwk
from sqlalchemy import TEXT, Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from .Base import Base


class JWKKey(Base):
    __tablename__ = "jwks"

    kid: Mapped[str] = mapped_column(
        String(64), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    content: Mapped[str] = mapped_column(TEXT, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    def expires_soon(self, threshold_days: int = 7) -> bool:
        if self.expires_at is None:
            return False
        expires_at = self.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return (
            datetime.now(timezone.utc) + timedelta(days=threshold_days)
            > expires_at
        )

    @property
    def jwk(self) -> jwk.JWK:
        """
        返回完整JWK对象
        """
        full_key = jwk.JWK.from_json(self.content)
        return full_key

    @property
    def key(self) -> dict:
        """
        返回完整JWK字典
        """
        full_key = json.loads(self.content)
        return full_key

    @property
    def pubkey(self) -> dict:
        """
        返回JWK公钥字典
        """
        full_key = jwk.JWK.from_json(self.content)
        public_jwk_json = full_key.export(private_key=False, as_dict=True)
        return public_jwk_json
