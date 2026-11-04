"""Event logging model."""
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from ..extensions import db


class EventLog(db.Model):
    __tablename__ = "event_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    level: Mapped[str] = mapped_column(String(20), nullable=False, default="INFO")  # INFO, WARNING, ERROR, CRITICAL
    category: Mapped[str] = mapped_column(String(60), nullable=False, default="system")
    source: Mapped[str] = mapped_column(String(120), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int] = mapped_column(
        Integer, db.ForeignKey("users.id"), nullable=True
    )
    device_id: Mapped[int] = mapped_column(
        Integer, db.ForeignKey("devices.id"), nullable=True
    )
    ip_address: Mapped[str] = mapped_column(String(60), nullable=True)
    details: Mapped[str] = mapped_column(Text, nullable=True)  # JSON

    def __repr__(self):
        return f"<EventLog {self.level}/{self.category}: {self.message[:60]}>"