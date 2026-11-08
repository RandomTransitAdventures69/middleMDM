"""User and role models."""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db
from sqlalchemy import String, Integer, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from ..utils import utcnow


class Role(db.Model):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    permissions: Mapped[str] = mapped_column(Text, nullable=True)  # JSON list of permission strings

    users: Mapped[list["User"]] = db.relationship(
        "User", back_populates="role", cascade="all, delete-orphan"
    )

    def __init__(self, name, display_name, description=None, permissions=None):
        import json
        self.name = name
        self.display_name = display_name
        self.description = description
        self.permissions = json.dumps(permissions or [])

    def get_permissions(self):
        import json
        try:
            return json.loads(self.permissions or "[]")
        except (ValueError, TypeError):
            return []

    def has_permission(self, perm):
        return perm in self.get_permissions()

    def __repr__(self):
        return f"<Role {self.name}>"


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(200), nullable=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    last_login: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, onupdate=utcnow
    )
    role_id: Mapped[int] = mapped_column(
        Integer, db.ForeignKey("roles.id"), nullable=False
    )

    role: Mapped["Role"] = db.relationship("Role", back_populates="users")

    def __init__(self, username, password, role_id, email=None, display_name=None):
        self.username = username
        self.email = email
        self.display_name = display_name or username
        self.role_id = role_id
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_permission(self, perm):
        if self.role:
            return self.role.has_permission(perm)
        return False

    def __repr__(self):
        return f"<User {self.username}>"


# Default role definitions
DEFAULT_ROLES = {
    "super_admin": {
        "display_name": "Super Administrator",
        "description": "Full access to all settings and management capabilities.",
        "permissions": [
            "devices:read", "devices:create", "devices:edit", "devices:delete",
            "devices:enroll", "devices:revoke", "devices:remote_lock",
            "groups:read", "groups:create", "groups:edit", "groups:delete",
            "policies:read", "policies:create", "policies:edit", "policies:delete",
            "policies:apply",
            "software:read",
            "users:read", "users:create", "users:edit", "users:delete",
            "settings:read", "settings:edit",
            "events:read", "events:delete",
            "system:read",
            "api:read", "api:manage",
        ],
    },
    "admin": {
        "display_name": "Administrator",
        "description": "Can manage devices, groups, policies, and users.",
        "permissions": [
            "devices:read", "devices:create", "devices:edit", "devices:delete",
            "devices:enroll", "devices:revoke", "devices:remote_lock",
            "groups:read", "groups:create", "groups:edit", "groups:delete",
            "policies:read", "policies:create", "policies:edit", "policies:delete",
            "policies:apply",
            "software:read",
            "users:read", "users:create", "users:edit",
            "events:read",
            "api:read",
        ],
    },
    "technician": {
        "display_name": "IT Technician",
        "description": "Can view and manage devices, apply policies.",
        "permissions": [
            "devices:read", "devices:edit", "devices:revoke",
            "groups:read",
            "policies:read", "policies:apply",
            "software:read",
            "events:read",
        ],
    },
    "viewer": {
        "display_name": "Viewer",
        "description": "Read-only access to the dashboard.",
        "permissions": [
            "devices:read",
            "groups:read",
            "policies:read",
            "software:read",
            "events:read",
            "system:read",
        ],
    },
}