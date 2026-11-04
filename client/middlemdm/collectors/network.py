"""Network information collector."""
import psutil
import socket


def get_interfaces():
    interfaces = []
    try:
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        
        for iface_name, addr_list in addrs.items():
            ip_addresses = []
            mac_address = None
            
            for addr in addr_list:
                if addr.family.name == 'AF_INET' and addr.address:
                    ip_addresses.append(addr.address)
                elif addr.family.name == 'AF_INET6' and addr.address:
                    if not addr.address.startswith('fe80'):  # Skip link-local
                        ip_addresses.append(addr.address)
                elif hasattr(addr.family, 'name') and 'AF_LINK' in str(addr.family) or addr.family == -1:
                    mac_address = addr.address
            
            is_active = False
            if iface_name in stats:
                is_active = stats[iface_name].isup
            
            interfaces.append({
                "name": iface_name,
                "mac_address": mac_address,
                "ip_addresses": ip_addresses,
                "is_active": is_active,
            })
    except Exception:
        pass
    return interfaces
