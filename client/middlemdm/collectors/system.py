"""System information collector."""
import platform
import psutil
import os
import time


def get_manufacturer():
    try:
        import wmi
        c = wmi.WMI()
        for system in c.Win32_ComputerSystem():
            return system.Manufacturer
    except Exception:
        pass
    return None


def get_model():
    try:
        import wmi
        c = wmi.WMI()
        for system in c.Win32_ComputerSystem():
            return system.Model
    except Exception:
        pass
    return None


def get_serial():
    try:
        import wmi
        c = wmi.WMI()
        for system in c.Win32_BIOS():
            return system.SerialNumber
    except Exception:
        pass
    return None


def get_cpu_info():
    try:
        return platform.processor()
    except Exception:
        return None


def get_cpu_cores():
    try:
        return psutil.cpu_count(logical=False) or psutil.cpu_count()
    except Exception:
        return None


def get_total_ram():
    try:
        return psutil.virtual_memory().total
    except Exception:
        return None


def get_uptime():
    try:
        return int(time.time() - psutil.boot_time())
    except Exception:
        return None


def get_storage():
    storage_list = []
    try:
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                storage_list.append({
                    "model": partition.device,
                    "interface_type": partition.fstype,
                    "total_bytes": usage.total,
                    "free_bytes": usage.free,
                    "is_system": partition.mountpoint == os.environ.get('SystemDrive', 'C:') + '\\',
                })
            except Exception:
                continue
    except Exception:
        pass
    return storage_list
