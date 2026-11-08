"""Client configuration."""
import json
import os
from pathlib import Path
from urllib.parse import urlsplit

CONFIG_DIR = Path(os.environ.get("PROGRAMDATA", "C:\\ProgramData")) / "middleMDM"
CONFIG_FILE = CONFIG_DIR / "config.json"


DEFAULT_CONFIG = {
    "server_url": "https://mdm.example",
    "allow_insecure_http": False,
    "device_id": None,
    "api_token": None,
    "enrollment_secret": None,
    "heartbeat_interval": 300,
    "inventory_interval": 3600,
}


def validate_server_url(server_url, allow_insecure_http=False):
    """Require HTTPS except for explicitly enabled loopback development servers."""
    if not isinstance(server_url, str) or not server_url.strip():
        raise ValueError("server_url must be a non-empty HTTPS URL")

    try:
        parsed = urlsplit(server_url.strip())
        hostname = parsed.hostname
        parsed.port
    except ValueError as exc:
        raise ValueError("server_url must be a valid HTTPS URL") from exc

    if not hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("server_url must be a valid HTTPS URL without credentials or query values")

    if parsed.scheme == "https":
        return server_url.strip().rstrip("/")

    loopback_hosts = {"localhost", "127.0.0.1", "::1"}
    if (
        parsed.scheme == "http"
        and allow_insecure_http is True
        and hostname.lower() in loopback_hosts
    ):
        return server_url.strip().rstrip("/")

    raise ValueError(
        "server_url must use HTTPS; HTTP is allowed only for explicitly enabled loopback development"
    )


def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding="utf-8") as f:
            saved_config = json.load(f)
        if not isinstance(saved_config, dict):
            raise ValueError("Client configuration must contain a JSON object")
        config = DEFAULT_CONFIG.copy()
        config.update(saved_config)
    else:
        config = DEFAULT_CONFIG.copy()

    config["server_url"] = validate_server_url(
        config.get("server_url"),
        config.get("allow_insecure_http", False),
    )
    return config


def save_config(config):
    config = config.copy()
    config["server_url"] = validate_server_url(
        config.get("server_url"),
        config.get("allow_insecure_http", False),
    )
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding="utf-8") as f:
        json.dump(config, f, indent=2)
