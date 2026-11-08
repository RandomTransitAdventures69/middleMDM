"""Plain-English label helpers for the admin UI."""
from datetime import datetime, timezone

# Plain-English status labels with technical term for tooltips/details
DEVICE_STATUS_LABELS = {
    "online": {"label": "Online recently", "technical": "Last contacted server within threshold"},
    "offline": {"label": "Offline", "technical": "No recent check-in"},
    "revoked": {"label": "Removed from management", "technical": "Enrollment revoked"},
    "needs_attention": {"label": "Needs attention", "technical": "Has issues requiring review"},
    "setup_incomplete": {"label": "Setup incomplete", "technical": "Enrollment or initial inventory pending"},
    "managed": {"label": "Managed", "technical": "Enrolled and reporting"},
}

POLICY_RESULT_LABELS = {
    "compliant": {"label": "Meets requirements", "technical": "compliant"},
    "non_compliant": {"label": "Does not meet requirements", "technical": "non_compliant"},
    "error": {"label": "Could not apply", "technical": "error"},
    "pending": {"label": "Waiting for device", "technical": "pending"},
}

TERMINOLOGY = {
    "enrollment": {"label": "Add device to management", "technical": "Enrollment"},
    "checkin": {"label": "Last contacted server", "technical": "Device check-in"},
    "policy_assignment": {"label": "Devices receiving these settings", "technical": "Policy assignment"},
    "remediation": {"label": "Try to fix", "technical": "Remediation"},
    "conflict": {"label": "Conflicting settings", "technical": "Conflict"},
    "configuration_profile": {"label": "Settings profile", "technical": "Configuration profile"},
}


def get_device_status_info(device):
    """Return plain-English status info for a device."""
    if device.revoked:
        return {"key": "revoked", **DEVICE_STATUS_LABELS["revoked"]}
    if not device.last_checkin:
        return {"key": "setup_incomplete", **DEVICE_STATUS_LABELS["setup_incomplete"]}
    # Check for policy failures
    failed = [r for r in getattr(device, 'policy_results', []) or [] if r.status in ('non_compliant', 'error')]
    if failed:
        return {"key": "needs_attention", **DEVICE_STATUS_LABELS["needs_attention"], "count": len(failed)}
    if device.is_online:
        return {"key": "online", **DEVICE_STATUS_LABELS["online"]}
    return {"key": "offline", **DEVICE_STATUS_LABELS["offline"]}


def get_policy_result_label(status):
    return POLICY_RESULT_LABELS.get(status, {"label": status.replace("_", " ").title(), "technical": status})


def format_last_contact(dt):
    if not dt:
        return "Never contacted"
    return dt.strftime('%Y-%m-%d %H:%M')
