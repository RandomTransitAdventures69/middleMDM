"""Dashboard blueprint."""
from datetime import datetime, timedelta
from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from ..models.device import Device, DeviceGroup
from ..models.policy import Policy, PolicyResult
from ..models.event import EventLog
from ..models.inventory import InstalledSoftware
from ..utils import permission_required
from ..utils.labels import get_device_status_info, get_policy_result_label, format_last_contact

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/")
@login_required
@permission_required("system:read")
def index():
    """Main dashboard view."""
    all_devices = Device.query.all()
    total_devices = len(all_devices)
    online_devices = [d for d in all_devices if d.is_online]
    offline_devices = [d for d in all_devices if not d.is_online and d.last_checkin]
    never_checked_in = [d for d in all_devices if not d.last_checkin and not d.revoked]
    needs_attention = [d for d in all_devices if get_device_status_info(d)["key"] == "needs_attention"]

    # Failed policy results (latest per device/policy context simplified)
    failed_results = PolicyResult.query.filter(PolicyResult.status.in_(["non_compliant", "error"])).order_by(PolicyResult.reported_at.desc()).limit(10).all()

    # Alerts
    now = datetime.utcnow()
    stale_threshold = now - timedelta(hours=24)
    alerts = []
    for d in all_devices:
        if d.revoked:
            continue
        if not d.last_checkin:
            alerts.append({"type": "enrollment", "severity": "warning", "device": d, "title": "Setup incomplete", "message": f"{d.hostname or d.device_id} has been added but has not contacted the server yet."})
        elif d.last_checkin < stale_threshold:
            alerts.append({"type": "checkin", "severity": "warning", "device": d, "title": "Device has not checked in recently", "message": f"{d.hostname or d.device_id} last contacted the server on {format_last_contact(d.last_checkin)}."})
    for r in failed_results[:5]:
        device = r.device
        if device and not device.revoked:
            status_label = get_policy_result_label(r.status)["label"]
            alerts.append({"type": "policy", "severity": "error", "device": device, "title": f"Settings could not be applied", "message": f"{device.hostname or device.device_id}: {status_label}. {r.detail or 'No details provided.'}"})

    groups = DeviceGroup.query.count()
    policies = Policy.query.count()
    recent_events = EventLog.query.order_by(EventLog.timestamp.desc()).limit(10).all()
    recent_devices = Device.query.order_by(Device.last_checkin.desc().nullslast()).limit(8).all()

    return render_template(
        "dashboard/index.html",
        total_devices=total_devices,
        online_count=len(online_devices),
        offline_count=len(offline_devices),
        needs_attention_count=len(needs_attention),
        failed_settings_count=len(failed_results),
        never_checked_in_count=len(never_checked_in),
        groups=groups,
        policies=policies,
        recent_events=recent_events,
        recent_devices=recent_devices,
        alerts=alerts[:8],
        get_device_status_info=get_device_status_info,
        format_last_contact=format_last_contact,
    )


@dashboard_bp.route("/devices")
@login_required
@permission_required("devices:read")
def devices():
    """Device list view."""
    q = (request.args.get("q") or "").strip().lower()
    status_filter = request.args.get("status") or ""
    all_devices = Device.query.order_by(Device.hostname.asc().nullslast()).all()

    # Filter
    filtered = []
    for d in all_devices:
        info = get_device_status_info(d)
        if status_filter and info["key"] != status_filter:
            continue
        if q:
            hay = " ".join([d.hostname or "", d.device_id or "", d.os_name or "", d.manufacturer or "", d.model or ""]).lower()
            if q not in hay:
                continue
        filtered.append((d, info))

    return render_template(
        "dashboard/devices.html",
        devices=filtered,
        q=q,
        status_filter=status_filter,
        format_last_contact=format_last_contact,
    )


@dashboard_bp.route("/devices/<int:device_id>")
@login_required
@permission_required("devices:read")
def device_detail(device_id):
    """Device detail view."""
    device = Device.query.get_or_404(device_id)
    status_info = get_device_status_info(device)
    policy_results = PolicyResult.query.filter_by(device_id=device.id).order_by(PolicyResult.reported_at.desc()).limit(20).all()
    events = EventLog.query.filter_by(device_id=device.id).order_by(EventLog.timestamp.desc()).limit(20).all()
    return render_template(
        "dashboard/device_detail.html",
        device=device,
        status_info=status_info,
        policy_results=policy_results,
        events=events,
        get_policy_result_label=get_policy_result_label,
        format_last_contact=format_last_contact,
    )


@dashboard_bp.route("/alerts")
@login_required
@permission_required("events:read")
def alerts():
    """Alerts view."""
    all_devices = Device.query.all()
    now = datetime.utcnow()
    stale_threshold = now - timedelta(hours=24)
    alerts_list = []
    for d in all_devices:
        if d.revoked:
            continue
        if not d.last_checkin:
            alerts_list.append({"type": "enrollment", "severity": "warning", "device": d, "title": "Setup incomplete", "message": f"{d.hostname or d.device_id} has been added but has not contacted the server yet.", "detail": "Technical: No last_checkin recorded. The device agent may not be installed or cannot reach the server."})
        elif d.last_checkin < stale_threshold:
            alerts_list.append({"type": "checkin", "severity": "warning", "device": d, "title": "Device has not checked in recently", "message": f"{d.hostname or d.device_id} last contacted the server on {format_last_contact(d.last_checkin)}.", "detail": f"Technical: last_checkin={d.last_checkin.isoformat()} UTC, threshold=24h"})
    failed_results = PolicyResult.query.filter(PolicyResult.status.in_(["non_compliant", "error"])).order_by(PolicyResult.reported_at.desc()).limit(50).all()
    for r in failed_results:
        device = r.device
        if device and not device.revoked:
            status_label = get_policy_result_label(r.status)["label"]
            alerts_list.append({"type": "policy", "severity": "error", "device": device, "title": "Settings could not be applied", "message": f"{device.hostname or device.device_id}: {status_label}.", "detail": f"Technical: policy_id={r.policy_id}, status={r.status}, detail={r.detail or 'none'}", "result": r})
    return render_template("dashboard/alerts.html", alerts=alerts_list, format_last_contact=format_last_contact)


@dashboard_bp.route("/groups")
@login_required
@permission_required("groups:read")
def groups():
    groups = DeviceGroup.query.all()
    return render_template("dashboard/groups.html", groups=groups)


@dashboard_bp.route("/network")
@login_required
@permission_required("devices:read")
def network():
    devices = Device.query.all()
    return render_template("dashboard/network.html", devices=devices)


@dashboard_bp.route("/ip-assignments")
@login_required
@permission_required("devices:read")
def ip_assignments():
    devices = Device.query.all()
    return render_template("dashboard/ip_assignments.html", devices=devices)


@dashboard_bp.route("/software")
@login_required
@permission_required("software:read")
def software():
    software = InstalledSoftware.query.order_by(InstalledSoftware.name.asc()).all()
    return render_template("dashboard/software.html", software=software)


@dashboard_bp.route("/policies")
@login_required
@permission_required("policies:read")
def policies():
    policies = Policy.query.order_by(Policy.name.asc()).all()
    return render_template("dashboard/policies.html", policies=policies)


@dashboard_bp.route("/events")
@login_required
@permission_required("events:read")
def events():
    events = EventLog.query.order_by(EventLog.timestamp.desc()).limit(100).all()
    return render_template("dashboard/events.html", events=events)


@dashboard_bp.route("/settings")
@login_required
@permission_required("settings:read")
def settings():
    return render_template("dashboard/settings.html")


@dashboard_bp.route("/users")
@login_required
@permission_required("users:read")
def users():
    from ..models.user import User
    users = User.query.all()
    return render_template("dashboard/users.html", users=users)
