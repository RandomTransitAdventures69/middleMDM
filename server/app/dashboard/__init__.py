"""Dashboard blueprint."""
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from ..models.device import Device
from ..models.device import DeviceGroup
from ..models.policy import Policy
from ..models.event import EventLog
from ..models.inventory import InstalledSoftware
from ..utils import permission_required

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/")
@login_required
@permission_required("system:read")
def index():
    """Main dashboard view."""
    total_devices = Device.query.count()
    online_devices = sum(1 for d in Device.query.all() if d.is_online)
    offline_devices = total_devices - online_devices
    groups = DeviceGroup.query.count()
    policies = Policy.query.count()
    recent_events = EventLog.query.order_by(EventLog.timestamp.desc()).limit(10).all()
    recent_devices = Device.query.order_by(Device.last_checkin.desc()).limit(10).all()
    
    return render_template(
        "dashboard/index.html",
        total_devices=total_devices,
        online_devices=online_devices,
        offline_devices=offline_devices,
        groups=groups,
        policies=policies,
        recent_events=recent_events,
        recent_devices=recent_devices,
    )


@dashboard_bp.route("/devices")
@login_required
@permission_required("devices:read")
def devices():
    """Device list view."""
    devices = Device.query.order_by(Device.hostname).all()
    return render_template("dashboard/devices.html", devices=devices)


@dashboard_bp.route("/devices/<int:device_id>")
@login_required
@permission_required("devices:read")
def device_detail(device_id):
    """Device detail view."""
    device = Device.query.get_or_404(device_id)
    return render_template("dashboard/device_detail.html", device=device)


@dashboard_bp.route("/groups")
@login_required
@permission_required("groups:read")
def groups():
    """Device groups view."""
    groups = DeviceGroup.query.all()
    return render_template("dashboard/groups.html", groups=groups)


@dashboard_bp.route("/network")
@login_required
@permission_required("devices:read")
def network():
    """Network discovery view."""
    devices = Device.query.all()
    return render_template("dashboard/network.html", devices=devices)


@dashboard_bp.route("/ip-assignments")
@login_required
@permission_required("devices:read")
def ip_assignments():
    """IP assignments view."""
    devices = Device.query.all()
    return render_template("dashboard/ip_assignments.html", devices=devices)


@dashboard_bp.route("/software")
@login_required
@permission_required("software:read")
def software():
    """Software inventory view."""
    software = InstalledSoftware.query.all()
    return render_template("dashboard/software.html", software=software)


@dashboard_bp.route("/policies")
@login_required
@permission_required("policies:read")
def policies():
    """Policy management view."""
    policies = Policy.query.all()
    return render_template("dashboard/policies.html", policies=policies)


@dashboard_bp.route("/events")
@login_required
@permission_required("events:read")
def events():
    """Activity logs view."""
    events = EventLog.query.order_by(EventLog.timestamp.desc()).limit(100).all()
    return render_template("dashboard/events.html", events=events)


@dashboard_bp.route("/settings")
@login_required
@permission_required("settings:read")
def settings():
    """Server settings view."""
    return render_template("dashboard/settings.html")


@dashboard_bp.route("/users")
@login_required
@permission_required("users:read")
def users():
    """Administrator accounts view."""
    from ..models.user import User
    users = User.query.all()
    return render_template("dashboard/users.html", users=users)
