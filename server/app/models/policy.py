"""Policy models."""
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, Text, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..extensions import db


class Policy(db.Model):
    __tablename__ = "policies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(60), nullable=False, default="other")
    policy_type: Mapped[str] = mapped_column(String(60), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    configuration: Mapped[str] = mapped_column(Text, nullable=True)  # JSON
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    assignments: Mapped[list["PolicyAssignment"]] = db.relationship(
        "PolicyAssignment", back_populates="policy", cascade="all, delete-orphan"
    )

    def get_config(self):
        import json
        try:
            return json.loads(self.configuration or "{}")
        except (ValueError, TypeError):
            return {}

    def __repr__(self):
        return f"<Policy {self.name}>"


class PolicyAssignment(db.Model):
    __tablename__ = "policy_assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    policy_id: Mapped[int] = mapped_column(
        Integer, db.ForeignKey("policies.id"), nullable=False
    )
    device_id: Mapped[int] = mapped_column(
        Integer, db.ForeignKey("devices.id"), nullable=True
    )
    group_id: Mapped[int] = mapped_column(
        Integer, db.ForeignKey("device_groups.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    policy: Mapped["Policy"] = db.relationship("Policy", back_populates="assignments")

    __table_args__ = (
        db.UniqueConstraint("policy_id", "device_id", "group_id", name="uq_policy_assign"),
    )

    def __repr__(self):
        return f"<PolicyAssignment policy={self.policy_id}>"


class PolicyResult(db.Model):
    __tablename__ = "policy_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    device_id: Mapped[int] = mapped_column(
        Integer, db.ForeignKey("devices.id"), nullable=False
    )
    policy_id: Mapped[int] = mapped_column(
        Integer, db.ForeignKey("policies.id"), nullable=False
    )
    policy_type: Mapped[str] = mapped_column(String(60), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # compliant, non_compliant, error
    detail: Mapped[str] = mapped_column(Text, nullable=True)
    reported_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    device: Mapped["Device"] = db.relationship("Device", back_populates="policy_results")

    def __repr__(self):
        return f"<PolicyResult device={self.device_id} policy={self.policy_id} status={self.status}>"