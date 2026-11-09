"""Cross-platform system information collectors."""
import json
import os
import platform
import subprocess
import time
from functools import lru_cache
from pathlib import Path

import psutil


@lru_cache(maxsize=1)
def _mac_hardware_info():
    try:
        result = subprocess.run(
            ["system_profiler", "-json", "SPHardwareDataType"],
            check=True,
            capture_output=True,
            text=True,
            timeout=20,
        )
        data = json.loads(result.stdout)
        sections = data.get("SPHardwareDataType") if isinstance(data, dict) else None
        if isinstance(sections, list) and sections and isinstance(sections[0], dict):
            return sections[0]
    except (OSError, subprocess.SubprocessError, ValueError, TypeError):
        pass
    return {}


def _windows_wmi_value(class_name, property_name):
    try:
        import wmi

        entries = getattr(wmi.WMI(), class_name)()
        for entry in entries:
            value = getattr(entry, property_name, None)
            if value:
                return str(value).strip()
    except (ImportError, OSError, AttributeError):
        return None
    except Exception:
        return None
    return None


def _read_dmi_value(name):
    try:
        value = (Path("/sys/class/dmi/id") / name).read_text(encoding="utf-8").strip()
        if value and value.lower() not in {"none", "unknown", "to be filled by o.e.m."}:
            return value
    except OSError:
        pass
    return None


def get_manufacturer():
    system_name = platform.system()
    if system_name == "Windows":
        return _windows_wmi_value("Win32_ComputerSystem", "Manufacturer")
    if system_name == "Darwin":
        return "Apple"
    if system_name == "Linux":
        return _read_dmi_value("sys_vendor")
    return None


def get_model():
    system_name = platform.system()
    if system_name == "Windows":
        return _windows_wmi_value("Win32_ComputerSystem", "Model")
    if system_name == "Darwin":
        info = _mac_hardware_info()
        return info.get("machine_model_name") or info.get("machine_model")
    if system_name == "Linux":
        return _read_dmi_value("product_name")
    return None


def get_serial():
    system_name = platform.system()
    if system_name == "Windows":
        return _windows_wmi_value("Win32_BIOS", "SerialNumber")
    if system_name == "Darwin":
        return _mac_hardware_info().get("serial_number")
    if system_name == "Linux":
        return _read_dmi_value("product_serial")
    return None


def get_machine_id():
    """Return a stable platform identifier when the OS exposes one."""
    system_name = platform.system()
    if system_name == "Windows":
        return _windows_wmi_value("Win32_ComputerSystemProduct", "UUID")
    if system_name == "Darwin":
        info = _mac_hardware_info()
        return info.get("hardware_uuid") or info.get("platform_UUID")
    if system_name == "Linux":
        for path in (
            Path("/etc/machine-id"),
            Path("/var/lib/dbus/machine-id"),
        ):
            try:
                value = path.read_text(encoding="ascii").strip()
                if value:
                    return value
            except OSError:
                continue
        return _read_dmi_value("product_uuid")
    return None


def get_cpu_info():
    processor = platform.processor().strip()
    if processor:
        return processor

    if platform.system() == "Darwin":
        try:
            result = subprocess.run(
                ["sysctl", "-n", "machdep.cpu.brand_string"],
                check=True,
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.stdout.strip() or platform.machine()
        except (OSError, subprocess.SubprocessError):
            return platform.machine() or None

    if platform.system() == "Linux":
        try:
            for line in Path("/proc/cpuinfo").read_text(encoding="utf-8").splitlines():
                if line.lower().startswith(("model name", "hardware")):
                    return line.split(":", 1)[-1].strip()
        except OSError:
            pass
    return platform.machine() or None


def get_cpu_cores():
    try:
        return psutil.cpu_count(logical=False) or psutil.cpu_count()
    except (OSError, RuntimeError):
        return None


def get_total_ram():
    try:
        return psutil.virtual_memory().total
    except (OSError, RuntimeError):
        return None


def get_uptime():
    try:
        return max(0, int(time.time() - psutil.boot_time()))
    except (OSError, RuntimeError):
        return None


def get_storage():
    storage_list = []
    try:
        partitions = psutil.disk_partitions()
    except (OSError, RuntimeError):
        return storage_list

    system_name = platform.system()
    system_drive = os.environ.get("SystemDrive", "C:") + os.sep
    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
        except (OSError, PermissionError):
            continue

        if system_name == "Windows":
            is_system = os.path.normcase(os.path.normpath(partition.mountpoint)) == os.path.normcase(
                os.path.normpath(system_drive)
            )
        else:
            is_system = os.path.normpath(partition.mountpoint) == os.path.sep

        storage_list.append({
            "model": partition.device,
            "interface_type": partition.fstype,
            "total_bytes": usage.total,
            "free_bytes": usage.free,
            "is_system": is_system,
        })
    return storage_list
