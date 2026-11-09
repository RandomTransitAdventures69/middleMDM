"""Installed software collectors for Windows, macOS, and Linux."""
import platform
import plistlib
import shutil
import subprocess
from pathlib import Path


def _append_software(software, name, version=None, publisher=None):
    if name and not any(item["name"] == name for item in software):
        software.append({
            "name": str(name),
            "version": str(version) if version else None,
            "publisher": str(publisher) if publisher else None,
        })


def _windows_software():
    try:
        import winreg
    except ImportError:
        return []

    software = []
    registry_paths = (
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
    )
    for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        for path in registry_paths:
            try:
                root_key = winreg.OpenKey(hive, path)
            except OSError:
                continue
            try:
                entry_count = winreg.QueryInfoKey(root_key)[0]
                for index in range(entry_count):
                    try:
                        subkey_name = winreg.EnumKey(root_key, index)
                        subkey = winreg.OpenKey(root_key, subkey_name)
                    except OSError:
                        continue
                    try:
                        name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                        version = _registry_value(winreg, subkey, "DisplayVersion")
                        publisher = _registry_value(winreg, subkey, "Publisher")
                        _append_software(software, name, version, publisher)
                    except OSError:
                        continue
                    finally:
                        winreg.CloseKey(subkey)
            finally:
                winreg.CloseKey(root_key)
    return software


def _registry_value(winreg, key, name):
    try:
        return winreg.QueryValueEx(key, name)[0]
    except OSError:
        return None


def _macos_software():
    software = []
    application_dirs = (
        Path("/Applications"),
        Path("/System/Applications"),
        Path.home() / "Applications",
    )
    for directory in application_dirs:
        try:
            applications = directory.iterdir()
            for app_bundle in applications:
                if app_bundle.suffix.lower() != ".app":
                    continue
                info_path = app_bundle / "Contents" / "Info.plist"
                try:
                    with info_path.open("rb") as info_file:
                        info = plistlib.load(info_file)
                except (OSError, plistlib.InvalidFileException):
                    continue

                _append_software(
                    software,
                    info.get("CFBundleDisplayName") or info.get("CFBundleName") or app_bundle.stem,
                    info.get("CFBundleShortVersionString") or info.get("CFBundleVersion"),
                    info.get("CFBundleIdentifier"),
                )
        except OSError:
            continue
    return software


def _run_package_query(command):
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    return [line for line in result.stdout.splitlines() if line.strip()]


def _linux_software():
    software = []
    if shutil.which("dpkg-query"):
        lines = _run_package_query([
            "dpkg-query",
            "-W",
            "-f=${binary:Package}\\t${Version}\\t${Maintainer}\\n",
        ])
        for line in lines:
            fields = line.split("\t", 2)
            if fields:
                _append_software(
                    software,
                    fields[0],
                    fields[1] if len(fields) > 1 else None,
                    fields[2] if len(fields) > 2 else None,
                )
        return software

    if shutil.which("rpm"):
        lines = _run_package_query([
            "rpm",
            "-qa",
            "--qf",
            "%{NAME}\\t%{VERSION}-%{RELEASE}\\t%{VENDOR}\\n",
        ])
        for line in lines:
            fields = line.split("\t", 2)
            if fields:
                _append_software(
                    software,
                    fields[0],
                    fields[1] if len(fields) > 1 else None,
                    fields[2] if len(fields) > 2 else None,
                )
        return software

    if shutil.which("pacman"):
        for line in _run_package_query(["pacman", "-Q"]):
            fields = line.split(None, 1)
            if fields:
                _append_software(
                    software,
                    fields[0],
                    fields[1] if len(fields) > 1 else None,
                )
    return software


def get_installed_software():
    system_name = platform.system()
    if system_name == "Windows":
        return _windows_software()
    if system_name == "Darwin":
        return _macos_software()
    if system_name == "Linux":
        return _linux_software()
    return []
