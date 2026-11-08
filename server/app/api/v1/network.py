"""Network API."""
import json
from flask import request, jsonify
from . import api_bp
from .heartbeat import authenticate_device
from ...extensions import db
from ...models.inventory import NetworkInterface
from ...utils import utcnow


@api_bp.route("/network", methods=["POST"])
def report_network():
    """Report network information."""
    device = authenticate_device()
    if not device:
        return jsonify({"error": "Unauthorized"}), 401
    
    if device.revoked:
        return jsonify({"error": "Device revoked"}), 403
    
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    interfaces = data.get("network_interfaces")
    if not isinstance(interfaces, list) or any(
        not isinstance(interface, dict)
        or not isinstance(interface.get("ip_addresses", []), list)
        for interface in interfaces
    ):
        return jsonify({"error": "network_interfaces must be a list of valid interfaces"}), 400
    
    NetworkInterface.query.filter_by(device_id=device.id).delete()
    for interface in interfaces:
        db.session.add(NetworkInterface(
            device_id=device.id,
            name=interface.get("name"),
            mac_address=interface.get("mac_address"),
            ip_addresses=json.dumps(interface.get("ip_addresses", [])),
            is_active=interface.get("is_active", False),
        ))

    device.last_checkin = utcnow()
    device.status = "online"
    db.session.commit()

    return jsonify({"message": "Network information received"}), 200
