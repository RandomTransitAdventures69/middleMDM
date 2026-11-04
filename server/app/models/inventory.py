"""Inventory models."""
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..extensions import db


class DeviceInventory(db.Model):
    __tablename__ = "device_inventory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    device_id: Mapped[int] = mapped_column(
        Integer, db.ForeignKey("devices.id"), nullable=False
    )
    collected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    os_name: Mapped[str] = mapped_column(String(120), nullable=True)
    os_version: Mapped[str] = mapped_column(String(120), nullable=True)
    os_build: Mapped[str] = mapped_column(String(120), nullable=True)
    cpu: Mapped[str] = mapped_column(String(255), nullable=True)
    cpu_cores: Mapped[int] = mapped_column(Integer, nullable=True)
    total_ram_bytes: Mapped[int] = mapped_column(Integer, nullable=True)
    uptime_seconds: Mapped[int] = mapped_column(Integer, nullable=True)
    client_version: Mapped[str] = mapped_column(String(60), nullable=True)
    raw_data: Mapped[str] = mapped_column(Text, nullable=True)  # JSON blob

    device: Mapped["Device"] = db.relationship("Device", back_populates="inventories")

    def __repr__(self):
        return f"<DeviceInventory device={self.device_id} at={self.collected_at}>"


class StorageDevice(db.Model):
    __tablename__ = "storage_devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    device_id: Mapped[int] = mapped_column(
        Integer, db.ForeignKey("devices.id"), nullable=False
    )
    model: Mapped[str] = mapped_column(String(255), nullable=True)
    interface_type: Mapped[str] = mapped_column(String(60), nullable=True)
    total_bytes: Mapped[int] = mapped_column(Integer, nullable=True)
    free_bytes: Mapped[int] = mapped_column(Integer, nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    device: Mapped["Device"] = db.relationship("Device", back_populates="storage_devices")

    def __repr__(self):
        return f"<StorageDevice {self.model}>"


class NetworkInterface(db.Model):
    __tablename__ = "network_interfaces"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    device_id: Mapped[int] = mapped_column(
        Integer, db.ForeignKey("devices.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(120), nullable=True)
    mac_address: Mapped[str] = mapped_column(String(60), nullable=True)
    ip_addresses: Mapped[str] = mapped_column(Text, nullable=True)  # JSON list
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    device: Mapped["Device"] = db.relationship("Device", back_populates="network_interfaces")

    def get_ip_addresses(self):
        import json
        try:
            return json.loads(self.ip_addresses or "[]")
        except (ValueError, TypeError):
            return []

    def __repr__(self):
        return f"<NetworkInterface {self.name} mac={self.mac_address}>"


class InstalledSoftware(db.Model):
    __tablename__ = "installed_software"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    device_id: Mapped[int] = mapped_column(
        Integer, db.ForeignKey("devices.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(120), nullable=True)
    publisher: Mapped[str] = mapped_column(String(255), nullable=True)
    install_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    raw_data: Mapped[str] = mapped_column(Text, nullable=True)  # JSON blob

    device: Mapped["Device"] = db.relationship("Device", back_populates="installed_software")

    __table_args__ = (
        db.UniqueConstraint("device_id", "name", name="uq_device_software_name"),
    )

    def __repr__(self):
        return f"<InstalledSoftware {self.name} on device {self.device_id}>"