"""API token model for device authentication."""
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from ..extensions import db
from ..utils import utcnow
import secrets


class APIToken(db.Model):
    __tablename__ = "api_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    device_id: Mapped[int] = mapped_column(
        Integer, db.ForeignKey("devices.id"), nullable=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, db.ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    last_used: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    @staticmethod
    def generate_token():
        return secrets.token_urlsafe(48)

    @staticmethod
    def hash_token(token):
        import hashlib
        return hashlib.sha256(token.encode()).hexdigest()

    def is_valid(self):
        if self.revoked:
            return False
        if self.expires_at and utcnow() > self.expires_at:
            return False
        return True

    def __repr__(self):
        return f"<APIToken {self.name}>"