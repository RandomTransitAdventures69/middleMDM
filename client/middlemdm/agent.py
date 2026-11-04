"""Main agent for middleMDM client."""
import time
import uuid
import socket
import platform
from . import config
from .communication import api
from .collectors import system, network, software


class Agent:
    def __init__(self):
        self.config = config.load_config()
        self.running = False
    
    def get_device_id(self):
        if not self.config.get("device_id"):
            # Generate stable device ID based on machine
            try:
                # Try to get machine UUID
                import subprocess
                result = subprocess.run(['wmic', 'csproduct', 'get', 'UUID'], 
                                      capture_output=True, text=True)
                lines = result.stdout.strip().split('\n')
                if len(lines) >= 2 and lines[1].strip():
                    machine_uuid = lines[1].strip()
                else:
                    machine_uuid = str(uuid.getnode())
            except Exception:
                machine_uuid = str(uuid.getnode())
            self.config["device_id"] = f"WIN-{machine_uuid.replace('-', '')[:32].upper()}"
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
            "client_version": "0.1.0",
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
            "client_version": "0.1.0",
            "uptime_seconds": system.get_uptime(),
            "storage": system.get_storage(),
            "network_interfaces": network.get_interfaces(),
            "installed_software": software.get_installed_software(),
        }
        return api.update_inventory(inventory_data)
    
    def run(self):
        """Main agent loop."""
        self.running = True
        heartbeat_interval = self.config.get("heartbeat_interval", 300)
        inventory_interval = self.config.get("inventory_interval", 3600)
        
        last_heartbeat = 0
        last_inventory = 0
        
        while self.running:
            current_time = time.time()
            
            # Enroll if not enrolled
            if not self.config.get("api_token"):
                if self.enroll():
                    print("Enrolled successfully")
                else:
                    print("Enrollment failed, retrying...")
                    time.sleep(60)
                    continue
            
            # Send heartbeat
            if current_time - last_heartbeat >= heartbeat_interval:
                if self.send_heartbeat():
                    print("Heartbeat sent")
                else:
                    print("Heartbeat failed")
                last_heartbeat = current_time
            
            # Send inventory
            if current_time - last_inventory >= inventory_interval:
                if self.send_inventory():
                    print("Inventory sent")
                else:
                    print("Inventory failed")
                last_inventory = current_time
            
            time.sleep(10)
