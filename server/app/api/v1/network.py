"""Network API."""
from flask import request, jsonify
from datetime import datetime
import json
from . import api_bp
from .heartbeat import authenticate_device
from ...extensions import db
from ...models.device import Device


@api_bp.route("/network", methods=["POST"])
def report_network():
    """Report network information."""
    device = authenticate_device()
    if not device:
        return jsonify({"error": "Unauthorized"}), 401
    
    if device.revoked:
        return jsonify({"error": "Device revoked"}), 403
    
    data = request.get_json(silent=True) or {}
    
    device.last_checkin = datetime.utcnow()
    device.status = "online"
    db.session.commit()
    
    # Network info is stored via inventory updates, but this endpoint is for separate updates
    return jsonify({"message": "Network information received"}), 200
