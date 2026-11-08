"""Device enrollment API."""
from flask import request, jsonify, current_app
from . import api_bp
from ...extensions import db
from ...models.device import Device
from ...models.api_token import APIToken
from ...utils import log_event, utcnow


@api_bp.route("/enroll", methods=["POST"])
def enroll_device():
    """Enroll a new device."""
    data = request.get_json(silent=True) or {}
    
    enrollment_secret = data.get("enrollment_secret")
    if enrollment_secret != current_app.config.get("ENROLLMENT_SECRET"):
        log_event("WARNING", "enrollment", "Invalid enrollment secret", source="api", ip_address=request.remote_addr)
        return jsonify({"error": "Invalid enrollment secret"}), 401
    
    device_id = data.get("device_id")
    if not device_id:
        return jsonify({"error": "device_id required"}), 400
    
    hostname = data.get("hostname", "")
    os_name = data.get("os_name", "")
    os_version = data.get("os_version", "")
    
    # Check if already enrolled
    existing = Device.query.filter_by(device_id=device_id).first()
    if existing:
        if existing.revoked:
            return jsonify({"error": "Device enrollment revoked"}), 403
        # Re-enroll/update existing
        existing.hostname = hostname or existing.hostname
        existing.os_name = os_name or existing.os_name
        existing.os_version = os_version or existing.os_version
        existing.last_checkin = utcnow()
        db.session.commit()
        return jsonify({"message": "Device re-enrolled", "device_id": device_id}), 200
    
    # Create new device
    device = Device(
        device_id=device_id,
        hostname=hostname,
        os_name=os_name,
        os_version=os_version,
        os_build=data.get("os_build"),
        manufacturer=data.get("manufacturer"),
        model=data.get("model"),
        serial_number=data.get("serial_number"),
        cpu=data.get("cpu"),
        cpu_cores=data.get("cpu_cores"),
        total_ram_bytes=data.get("total_ram_bytes"),
        client_version=data.get("client_version"),
        status="online",
        last_checkin=utcnow(),
    )
    db.session.add(device)
    db.session.commit()
    
    # Generate API token for device
    token_plain = APIToken.generate_token()
    token = APIToken(
        token=token_plain,
        token_hash=APIToken.hash_token(token_plain),
        name=f"device-{device_id}",
        device_id=device.id,
    )
    db.session.add(token)
    db.session.commit()
    
    log_event("INFO", "enrollment", f"Device enrolled: {hostname} ({device_id})", source="api", device_id=device.id, ip_address=request.remote_addr)
    
    return jsonify({
        "message": "Device enrolled successfully",
        "device_id": device_id,
        "api_token": token_plain,
    }), 201
