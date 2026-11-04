"""middleMDM server configuration.

Secrets and operational settings are read from environment variables.
A local development configuration is provided as a default.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    """Base configuration shared by all environments."""

    # --- Core ---
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
    SESSION_COOKIE_NAME = os.environ.get("SESSION_COOKIE_NAME", "middlemdm_session")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "false").lower() == "true"

    # --- Database ---
    # Default to a local SQLite file for development. Production must set
    # DATABASE_URL to a PostgreSQL connection string.
    DATABASE_URL = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'middlemdm_dev.db'}",
    )

    # --- Application metadata ---
    APP_NAME = "middleMDM"
    APP_VERSION = "0.1.0"
    DEFAULT_TIMEZONE = os.environ.get("DEFAULT_TIMEZONE", "UTC")

    # --- API ---
    API_VERSION = "v1"
    API_TOKEN_EXPIRY_SECONDS = int(os.environ.get("API_TOKEN_EXPIRY_SECONDS", "86400"))

    # --- Device enrollment ---
    # Per-device enrollment secret. In production this is generated per device.
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

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    # Keep sessions secure only over HTTPS in production; dev allows http.
    SESSION_COOKIE_SECURE = False


class TestingConfig(Config):
    DEBUG = False
    TESTING = True
    DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "sqlite:///:memory:")
    SESSION_COOKIE_SECURE = False
    SECRET_KEY = "test-secret-key"
    ENROLLMENT_SECRET = "test-enrollment-secret"


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}