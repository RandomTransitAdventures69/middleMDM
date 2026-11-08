"""Flask application factory for middleMDM."""
from pathlib import Path
from flask import Flask, request, jsonify, render_template, redirect, url_for
from config import Config, config_by_name
from .extensions import csrf, init_extensions


def create_app(config_name="default"):
    """Create and configure the Flask application."""
    app = Flask(
        __name__,
        template_folder=str(Path(__file__).parent / "templates"),
        static_folder=str(Path(__file__).parent / "static"),
    )
    app.config.from_object(config_by_name.get(config_name, Config))

    # Initialize extensions
    init_extensions(app)

    # Register blueprints
    from .auth import auth_bp
    from .dashboard import dashboard_bp
    from .api.v1 import api_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(api_bp, url_prefix="/api/v1")
    csrf.exempt(api_bp)

    @app.route("/")
    def index():
        return redirect(url_for("dashboard.index"))

    # Register error handlers
    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Not found"}), 404
        return render_error_page(app, 404, "Page Not Found"), 404

    @app.errorhandler(500)
    def server_error(e):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Internal server error"}), 500
        return render_error_page(app, 500, "Internal Server Error"), 500

    @app.errorhandler(403)
    def forbidden(e):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Forbidden"}), 403
        return render_error_page(app, 403, "Access Denied"), 403

    # Context processors for templates
    @app.context_processor
    def inject_globals():
        from .models.settings import SystemSetting
        return {
            "app_name": app.config.get("APP_NAME", "middleMDM"),
            "app_version": app.config.get("APP_VERSION", "0.1.0"),
            "system_settings": SystemSetting,
        }

    # CLI command to initialize database
    @app.cli.command("init-db")
    def init_db():
        """Initialize the database with default roles and admin user."""
        from .models.user import User, Role, DEFAULT_ROLES
        from .models.settings import SystemSetting
        from .extensions import db

        db.create_all()

        # Create roles
        role_map = {}
        for key, info in DEFAULT_ROLES.items():
            role = Role.query.filter_by(name=key).first()
            if not role:
                role = Role(
                    name=key,
                    display_name=info["display_name"],
                    description=info["description"],
                    permissions=info["permissions"],
                )
                db.session.add(role)
            role_map[key] = role

        db.session.commit()

        # Create default admin if none exists
        if User.query.count() == 0:
            admin_role = role_map["super_admin"]
            admin = User(
                username="admin",
                password="admin123",
                role_id=admin_role.id,
                email="admin@middlemdm.local",
                display_name="Administrator",
            )
            db.session.add(admin)
            db.session.commit()
            print("Created default admin user 'admin' with password 'admin123'")

        # Set default settings
        defaults = {
            "checkin_interval": ("300", "integer", "Default device check-in interval in seconds"),
            "device_offline_threshold": ("600", "integer", "Seconds before a device is considered offline"),
            "session_timeout": ("3600", "integer", "Session timeout in seconds"),
            "enable_device_registration": ("true", "boolean", "Allow new device enrollment"),
            "max_devices_per_user": ("100", "integer", "Max devices a user can enroll"),
        }
        for key, (val, vtype, desc) in defaults.items():
            if SystemSetting.get(key) is None:
                SystemSetting.set(key, val, vtype, desc)

        print("Database initialized successfully.")

    return app


def render_error_page(app, code, message):
    """Render a simple error page."""
    try:
        return render_template("errors/%d.html" % code, message=message)
    except Exception:
        return f"<h1>{code} - {message}</h1>", code
