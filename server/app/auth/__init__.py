"""Authentication blueprint."""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_user, logout_user, current_user, login_required
from flask_wtf import CSRFProtect
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length
from ..extensions import db, login_manager
from ..models.user import User
from ..utils import log_event

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


class LoginForm:
    """Simple login form (using WTForms-like structure)."""
    def __init__(self):
        self.username = StringField("Username", validators=[DataRequired(), Length(max=80)])
        self.password = PasswordField("Password", validators=[DataRequired()])
        self.remember_me = BooleanField("Remember me")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        remember = request.form.get("remember_me") == "y"

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=remember)
            user.last_login = __import__("datetime").datetime.utcnow()
            db.session.commit()

            log_event(
                "INFO", "auth", f"User '{username}' logged in",
                source="web", user_id=user.id,
            )

            next_page = request.args.get("next")
            if next_page:
                return redirect(next_page)
            return redirect(url_for("dashboard.index"))
        else:
            error = "Invalid username or password."
            log_event(
                "WARNING", "auth", f"Failed login attempt for username '{username}'",
                source="web", ip_address=request.remote_addr,
            )

    return render_template("auth/login.html", form=form, error=error)


@auth_bp.route("/logout")
@login_required
def logout():
    username = current_user.username
    logout_user()
    session.clear()
    log_event("INFO", "auth", f"User '{username}' logged out", source="web")
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/health")
def health():
    """Health check endpoint for monitoring."""
    return jsonify({"status": "ok", "version": "0.1.0"})