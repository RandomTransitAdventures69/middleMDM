"""Device and device group models."""
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..extensions import db


class DeviceGroup(db.Model):
    __tablename__ = "device_groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    parent_id: Mapped[int] = mapped_column(
        Integer, db.ForeignKey("device_groups.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    memberships: Mapped[list["DeviceGroupMembership"]] = db.relationship(
        "DeviceGroupMembership", back_populates="group", cascade="all, delete-orphan"
    )
    children: Mapped[list["DeviceGroup"]] = db.relationship(
        "DeviceGroup", backref=db.backref("parent", remote_side=[id]), cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<DeviceGroup {self.name}>"


class DeviceGroupMembership(db.Model):
    __tablename__ = "device_group_memberships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    device_id: Mapped[int] = mapped_column(
        Integer, db.ForeignKey("devices.id"), nullable=False
    )
    group_id: Mapped[int] = mapped_column(
        Integer, db.ForeignKey("device_groups.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    device: Mapped["Device"] = db.relationship("Device", back_populates="memberships")
    group: Mapped["DeviceGroup"] = db.relationship("DeviceGroup", back_populates="memberships")

    __table_args__ = (db.UniqueConstraint("device_id", "group_id"),)

    def __repr__(self):
        return f"<DeviceGroupMembership device={self.device_id} group={self.group_id}>"


class Device(db.Model):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    device_id: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False, index=True
    )
    hostname: Mapped[str] = mapped_column(String(255), nullable=True)
    serial_number: Mapped[str] = mapped_column(String(255), nullable=True, index=True)
    manufacturer: Mapped[str] = mapped_column(String(120), nullable=True)
    model: Mapped[str] = mapped_column(String(255), nullable=True)
    os_name: Mapped[str] = mapped_column(String(120), nullable=True)
    os_version: Mapped[str] = mapped_column(String(120), nullable=True)
    os_build: Mapped[str] = mapped_column(String(120), nullable=True)
    cpu: Mapped[str] = mapped_column(String(255), nullable=True)
    cpu_cores: Mapped[int] = mapped_column(Integer, nullable=True)
    total_ram_bytes: Mapped[int] = mapped_column(Integer, nullable=True)
    client_version: Mapped[str] = mapped_column(String(60), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="offline", nullable=False)
    last_checkin: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    enrollment_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    revoked_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    inventories: Mapped[list["DeviceInventory"]] = db.relationship(
        "DeviceInventory", back_populates="device", cascade="all, delete-orphan"
    )
    storage_devices: Mapped[list["StorageDevice"]] = db.relationship(
        "StorageDevice", back_populates="device", cascade="all, delete-orphan"
    )
    network_interfaces: Mapped[list["NetworkInterface"]] = db.relationship(
        "NetworkInterface", back_populates="device", cascade="all, delete-orphan"
    )
    installed_software: Mapped[list["InstalledSoftware"]] = db.relationship(
        "InstalledSoftware", back_populates="device", cascade="all, delete-orphan"
    )
    memberships: Mapped[list["DeviceGroupMembership"]] = db.relationship(
        "DeviceGroupMembership", back_populates="device", cascade="all, delete-orphan"
    )
    policy_results: Mapped[list["PolicyResult"]] = db.relationship(
        "PolicyResult", back_populates="device", cascade="all, delete-orphan"
    )

    def get_groups(self):
        return [m.group for m in self.memberships]

    def set_groups(self, group_ids):
        self.memberships = [
            DeviceGroupMembership(device_id=self.id, group_id=gid) for gid in group_ids
        ]

    @property
    def is_online(self):
        if not self.last_checkin:
            return False
        return (datetime.utcnow() - self.last_checkin).total_seconds() < 600

    def __repr__(self):
        return f"<Device {self.device_id}>"
