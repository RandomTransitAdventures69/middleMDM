"""Cross-platform network interface collector."""
import ipaddress

import psutil


def get_interfaces():
    try:
        addresses = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
    except (OSError, RuntimeError):
        return []

    interfaces = []
    for interface_name, address_list in addresses.items():
        ip_addresses = []
        mac_address = None

        for address in address_list:
            family_name = getattr(address.family, "name", "")
            if family_name == "AF_INET" and address.address:
                ip_addresses.append(address.address)
            elif family_name == "AF_INET6" and address.address:
                ip = address.address.split("%", 1)[0]
                try:
                    if not ipaddress.ip_address(ip).is_link_local:
                        ip_addresses.append(address.address)
                except ValueError:
                    continue
            elif family_name in {"AF_LINK", "AF_PACKET"} or address.family == -1:
                mac_address = address.address

        interface_stats = stats.get(interface_name)
        interfaces.append({
            "name": interface_name,
            "mac_address": mac_address,
            "ip_addresses": ip_addresses,
            "is_active": bool(interface_stats and interface_stats.isup),
        })

    return interfaces
