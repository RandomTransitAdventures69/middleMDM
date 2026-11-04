"""Software inventory collector."""
import subprocess


def get_installed_software():
    software_list = []
    try:
        # Try to get installed programs from registry on Windows
        import winreg
        
        # Check both 32-bit and 64-bit registry views
        for hkey in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
            for subkey_path in [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
            ]:
                try:
                    key = winreg.OpenKey(hkey, subkey_path)
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            subkey = winreg.OpenKey(key, subkey_name)
                            try:
                                name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                try:
                                    version = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                                except Exception:
                                    version = None
                                try:
                                    publisher = winreg.QueryValueEx(subkey, "Publisher")[0]
                                except Exception:
                                    publisher = None
                                
                                if name and name not in [s['name'] for s in software_list]:
                                    software_list.append({
                                        "name": name,
                                        "version": version,
                                        "publisher": publisher,
                                    })
                            except Exception:
                                pass
                            finally:
                                winreg.CloseKey(subkey)
                        except Exception:
                            continue
                    winreg.CloseKey(key)
                except Exception:
                    continue
    except Exception:
        pass
    return software_list
