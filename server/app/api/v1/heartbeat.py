"""Heartbeat API."""
from flask import request, jsonify
from . import api_bp
from ...extensions import db
from ...models.device import Device
from ...models.api_token import APIToken
from ...utils import utcnow


def authenticate_device():
    """Authenticate device via API token."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token_plain = auth_header[7:]
    else:
        payload = request.get_json(silent=True)
        token_plain = request.headers.get("X-Device-Token") or (
            payload.get("api_token") if isinstance(payload, dict) else None
        )
    
    if not token_plain:
        return None
    
    token_hash = APIToken.hash_token(token_plain)
    token = APIToken.query.filter_by(token_hash=token_hash).first()
    
    if not token or not token.is_valid():
        return None
    
    token.last_used = utcnow()
    db.session.commit()
    
    if token.device_id:
        return db.session.get(Device, token.device_id)
    return None


@api_bp.route("/heartbeat", methods=["POST"])
def heartbeat():
    """Device heartbeat endpoint."""
    device = authenticate_device()
    if not device:
        return jsonify({"error": "Unauthorized"}), 401
    
    if device.revoked:
        return jsonify({"error": "Device revoked"}), 403
    
    device.last_checkin = utcnow()
    device.status = "online"
    db.session.commit()
    
    return jsonify({
        "status": "ok",
        "server_time": utcnow().isoformat(),
        "next_checkin": 300,
    }), 200
