"""API communication module."""
import requests
import json
from .. import config


def get_headers():
    cfg = config.load_config()
    headers = {"Content-Type": "application/json"}
    if cfg.get("api_token"):
        headers["Authorization"] = f"Bearer {cfg['api_token']}"
    return headers


def enroll(data):
    cfg = config.load_config()
    server_url = cfg.get("server_url")
    try:
        response = requests.post(f"{server_url}/api/v1/enroll", 
                               json=data, 
                               headers={"Content-Type": "application/json"},
                               timeout=30)
        if response.status_code in [200, 201]:
            return response.json()
        return None
    except Exception as e:
        print(f"Enrollment error: {e}")
        return None


def heartbeat():
    cfg = config.load_config()
    server_url = cfg.get("server_url")
    try:
        response = requests.post(f"{server_url}/api/v1/heartbeat",
                               headers=get_headers(),
                               timeout=30)
        return response.status_code == 200
    except Exception as e:
        print(f"Heartbeat error: {e}")
        return False


def update_inventory(data):
    cfg = config.load_config()
    server_url = cfg.get("server_url")
    try:
        response = requests.post(f"{server_url}/api/v1/inventory",
                               json=data,
                               headers=get_headers(),
                               timeout=60)
        return response.status_code == 200
    except Exception as e:
        print(f"Inventory error: {e}")
        return False
