"""Main agent for middleMDM client."""
import time
import uuid
import socket
import platform
import hashlib
import threading
from . import config
from . import __version__
from .communication import api
from .collectors import system, network, software


class Agent:
    def __init__(self):
        self.config = config.load_config()
        self.running = False
        self._stop_event = threading.Event()

    def get_device_id(self):
        if not self.config.get("device_id"):
            machine_id = str(system.get_machine_id() or uuid.uuid4().hex)
            device_hash = hashlib.sha256(machine_id.encode("utf-8")).hexdigest()[:32].upper()
            platform_prefix = {
                "Windows": "WIN",
                "Darwin": "MAC",
                "Linux": "LINUX",
            }.get(platform.system(), "DEVICE")
            self.config["device_id"] = f"{platform_prefix}-{device_hash}"
            config.save_config(self.config)
        return self.config["device_id"]

    def enroll(self):
        """Enroll device with server."""
        device_id = self.get_device_id()
        enrollment_data = {
            "enrollment_secret": self.config.get("enrollment_secret"),
            "device_id": device_id,
            "hostname": socket.gethostname(),
            "os_name": platform.system(),
            "os_version": platform.version(),
            "manufacturer": system.get_manufacturer(),
            "model": system.get_model(),
            "serial_number": system.get_serial(),
            "cpu": system.get_cpu_info(),
            "cpu_cores": system.get_cpu_cores(),
            "total_ram_bytes": system.get_total_ram(),
            "client_version": __version__,
        }

        response = api.enroll(enrollment_data)
        if response and response.get("api_token"):
            self.config["api_token"] = response["api_token"]
            config.save_config(self.config)
            return True
        return False

    def send_heartbeat(self):
        """Send heartbeat to server."""
        return api.heartbeat()

    def send_inventory(self):
        """Send full inventory to server."""
        inventory_data = {
            "hostname": socket.gethostname(),
            "os_name": platform.system(),
            "os_version": platform.version(),
            "os_build": platform.release(),
            "cpu": system.get_cpu_info(),
            "cpu_cores": system.get_cpu_cores(),
            "total_ram_bytes": system.get_total_ram(),
            "client_version": __version__,
            "uptime_seconds": system.get_uptime(),
            "storage": system.get_storage(),
            "network_interfaces": network.get_interfaces(),
            "installed_software": software.get_installed_software(),
        }
        return api.update_inventory(inventory_data)

    def run(self):
        """Main agent loop."""
        self.running = True
        self._stop_event.clear()
        heartbeat_interval = self.config.get("heartbeat_interval", 300)
        inventory_interval = self.config.get("inventory_interval", 3600)

        last_heartbeat = 0
        last_inventory = 0

        try:
            while self.running and not self._stop_event.is_set():
                current_time = time.time()

                if not self.config.get("api_token"):
                    if self.enroll():
                        print("Enrolled successfully")
                    else:
                        print("Enrollment failed, retrying...")
                        self._stop_event.wait(60)
                        continue

                if current_time - last_heartbeat >= heartbeat_interval:
                    if self.send_heartbeat():
                        print("Heartbeat sent")
                    else:
                        print("Heartbeat failed")
                    last_heartbeat = current_time

                if current_time - last_inventory >= inventory_interval:
                    if self.send_inventory():
                        print("Inventory sent")
                    else:
                        print("Inventory failed")
                    last_inventory = current_time

                self._stop_event.wait(10)
        finally:
            self.running = False

    def stop(self):
        """Stop the agent loop and interrupt its current wait."""
        self.running = False
        self._stop_event.set()
