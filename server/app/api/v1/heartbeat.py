"""Heartbeat API."""
from flask import request, jsonify
from datetime import datetime
from . import api_bp
from ...extensions import db
from ...models.device import Device
from ...models.api_token import APIToken
from ...utils import log_event


def authenticate_device():
    """Authenticate device via API token."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token_plain = auth_header[7:]
    else:
        token_plain = request.headers.get("X-Device-Token") or request.json.get("api_token") if request.is_json else None
    
    if not token_plain:
        return None
    
    token_hash = APIToken.hash_token(token_plain)
    token = APIToken.query.filter_by(token_hash=token_hash).first()
    
    if not token or not token.is_valid():
        return None
    
    token.last_used = datetime.utcnow()
    db.session.commit()
    
    if token.device_id:
        return Device.query.get(token.device_id)
    return None


@api_bp.route("/heartbeat", methods=["POST"])
def heartbeat():
    """Device heartbeat endpoint."""
    device = authenticate_device()
    if not device:
        return jsonify({"error": "Unauthorized"}), 401
    
    if device.revoked:
        return jsonify({"error": "Device revoked"}), 403
    
    device.last_checkin = datetime.utcnow()
    device.status = "online"
    db.session.commit()
    
    return jsonify({
        "status": "ok",
        "server_time": datetime.utcnow().isoformat(),
        "next_checkin": 300,
    }), 200
