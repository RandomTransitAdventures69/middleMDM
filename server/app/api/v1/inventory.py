"""Inventory API."""
from flask import request, jsonify
from datetime import datetime
import json
from . import api_bp
from .heartbeat import authenticate_device
from ...extensions import db
from ...models.device import Device
from ...models.inventory import DeviceInventory, StorageDevice, NetworkInterface, InstalledSoftware


@api_bp.route("/inventory", methods=["POST"])
def update_inventory():
    """Update device inventory."""
    device = authenticate_device()
    if not device:
        return jsonify({"error": "Unauthorized"}), 401
    
    if device.revoked:
        return jsonify({"error": "Device revoked"}), 403
    
    data = request.get_json(silent=True) or {}
    
    # Update device basic info
    device.hostname = data.get("hostname", device.hostname)
    device.os_name = data.get("os_name", device.os_name)
    device.os_version = data.get("os_version", device.os_version)
    device.os_build = data.get("os_build", device.os_build)
    device.cpu = data.get("cpu", device.cpu)
    device.cpu_cores = data.get("cpu_cores", device.cpu_cores)
    device.total_ram_bytes = data.get("total_ram_bytes", device.total_ram_bytes)
    device.client_version = data.get("client_version", device.client_version)
    device.last_checkin = datetime.utcnow()
    device.status = "online"
    
    # Create inventory snapshot
    inv = DeviceInventory(
        device_id=device.id,
        os_name=device.os_name,
        os_version=device.os_version,
        os_build=device.os_build,
        cpu=device.cpu,
        cpu_cores=device.cpu_cores,
        total_ram_bytes=device.total_ram_bytes,
        uptime_seconds=data.get("uptime_seconds"),
        client_version=device.client_version,
        raw_data=json.dumps(data),
    )
    db.session.add(inv)
    
    # Update storage
    StorageDevice.query.filter_by(device_id=device.id).delete()
    for storage in data.get("storage", []):
        sd = StorageDevice(
            device_id=device.id,
            model=storage.get("model"),
            interface_type=storage.get("interface_type"),
            total_bytes=storage.get("total_bytes"),
            free_bytes=storage.get("free_bytes"),
            is_system=storage.get("is_system", False),
        )
        db.session.add(sd)
    
    # Update network interfaces
    NetworkInterface.query.filter_by(device_id=device.id).delete()
    for iface in data.get("network_interfaces", []):
        ni = NetworkInterface(
            device_id=device.id,
            name=iface.get("name"),
            mac_address=iface.get("mac_address"),
            ip_addresses=json.dumps(iface.get("ip_addresses", [])),
            is_active=iface.get("is_active", False),
        )
        db.session.add(ni)
    
    # Update software
    # For now, replace all software (could be optimized with diffing)
    InstalledSoftware.query.filter_by(device_id=device.id).delete()
    for sw in data.get("installed_software", []):
        if sw.get("name"):
            sw_entry = InstalledSoftware(
                device_id=device.id,
                name=sw["name"],
                version=sw.get("version"),
                publisher=sw.get("publisher"),
                install_date=sw.get("install_date"),
                raw_data=json.dumps(sw),
            )
            db.session.add(sw_entry)
    
    db.session.commit()
    
    return jsonify({"message": "Inventory updated successfully"}), 200
