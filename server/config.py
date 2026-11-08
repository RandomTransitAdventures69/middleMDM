"""middleMDM server configuration.

Secrets and operational settings are read from environment variables.
A local development configuration is provided as a default.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    """Base configuration shared by all environments."""

    # --- Core ---
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
    SESSION_COOKIE_NAME = os.environ.get("SESSION_COOKIE_NAME", "middlemdm_session")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "false").lower() == "true"

    # --- Database ---
    DATABASE_URL = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'middlemdm_dev.db'}",
    )
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Application metadata ---
    APP_NAME = "middleMDM"
    APP_VERSION = "0.1.0"
    DEFAULT_TIMEZONE = os.environ.get("DEFAULT_TIMEZONE", "UTC")

    # --- API ---
    API_VERSION = "v1"
    API_TOKEN_EXPIRY_SECONDS = int(os.environ.get("API_TOKEN_EXPIRY_SECONDS", "86400"))

    # --- Device enrollment ---
    ENROLLMENT_SECRET = os.environ.get("ENROLLMENT_SECRET", "dev-enrollment-secret-change-me")

    # --- Email / SMTP (optional, for future account recovery) ---
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

    # --- Logging ---
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FILE = os.environ.get("LOG_FILE", str(BASE_DIR / "middlemdm.log"))

    # --- CORS ---
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")

    # CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_CHECK_DEFAULT = True

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = False  # Disable CSRF for API in dev if needed, but better to handle


class TestingConfig(Config):
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL", "sqlite:///:memory:")
    DATABASE_URL = SQLALCHEMY_DATABASE_URI
    SESSION_COOKIE_SECURE = False
    SECRET_KEY = "test-secret-key"
    ENROLLMENT_SECRET = "test-enrollment-secret"
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
