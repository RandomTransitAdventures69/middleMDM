"""Utility helpers."""
import json
import logging
from datetime import datetime, timezone
from functools import wraps
from flask import request, jsonify, current_app
from flask_login import current_user


def utcnow():
    """Return the current UTC time as a naive value for existing database columns."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def permission_required(perm):
    """Decorator to require a permission on a view."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated or not current_user.has_permission(perm):
                current_app.logger.warning(
                    f"Permission denied: {perm} for user {current_user.username if current_user.is_authenticated else 'anonymous'}"
                )
                return jsonify({"error": "Forbidden"}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator


def log_event(level, category, message, source=None, user_id=None, device_id=None, ip_address=None, details=None):
    """Create an event log entry."""
    from ..models.event import EventLog
    from ..extensions import db

    if isinstance(details, (dict, list)):
        details = json.dumps(details)
    elif details is not None:
        details = str(details)

    event = EventLog(
        level=level,
        category=category,
        message=message,
        source=source,
        user_id=user_id,
        device_id=device_id,
        ip_address=ip_address or request.remote_addr if request else None,
        details=details,
    )
    db.session.add(event)
    db.session.commit()
    return event


def get_client_ip():
    if not request:
        return None
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr


def format_bytes(num_bytes):
    """Format a byte count into a human-readable string."""
    if not num_bytes:
        return "0 B"
    for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} EB"


def format_uptime(seconds):
    """Format seconds into a human-readable uptime string."""
    if not seconds:
        return "Unknown"
    days, remainder = divmod(int(seconds), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, secs = divmod(remainder, 60)
    if days:
        return f"{days}d {hours}h {minutes}m"
    return f"{hours}h {minutes}m {secs}s"


def parse_bool(value, default=False):
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    return str(value).lower() in ("true", "1", "yes", "on", "t", "y")