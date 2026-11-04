"""Devices API."""
from flask import request, jsonify
from . import api_bp
from .heartbeat import authenticate_device


@api_bp.route("/devices/info", methods=["GET"])
def device_info():
    """Get device info."""
    device = authenticate_device()
    if not device:
        return jsonify({"error": "Unauthorized"}), 401
    
    return jsonify({
        "device_id": device.device_id,
        "hostname": device.hostname,
        "os_name": device.os_name,
        "os_version": device.os_version,
        "client_version": device.client_version,
    }), 200
