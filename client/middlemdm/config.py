"""Client configuration."""
import json
import os
from pathlib import Path

CONFIG_DIR = Path(os.environ.get("PROGRAMDATA", "C:\\ProgramData")) / "middleMDM"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_FILE = CONFIG_DIR / "config.json"


DEFAULT_CONFIG = {
    "server_url": "http://10.1.1.1:5001",
    "device_id": None,
    "api_token": None,
    "enrollment_secret": None,
    "heartbeat_interval": 300,
    "inventory_interval": 3600,
}


def load_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = DEFAULT_CONFIG.copy()
                config.update(json.load(f))
                return config
        except Exception:
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()


def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
