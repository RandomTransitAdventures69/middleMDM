# Networking Guide

## Network Requirements

middleMDM requires network connectivity between the server and clients.

### Ports
- Server web interface and API: TCP 5000 (configurable)
- For HTTPS in production: TCP 443

### Firewall Rules

**Server (Linux):**
```bash
sudo ufw allow from 10.1.1.0/24 to any port 5001
# Or allow all if needed
sudo ufw allow 5000/tcp
```

**Clients (Windows):**
Allow outbound connections to server on configured port.

## Static IP Configuration

Static IP addresses are required in the documented deployment configuration. The documentation explains how to configure static addresses on the server and enrolled clients.

### Example Network Layout

| Device | Address | Purpose |
|--------|---------|---------|
| Server | 10.1.1.1 | middleMDM Management Server |
| Client 01 | 10.1.1.10 | Managed Windows Client |
| Client 02 | 10.1.1.11 | Managed Windows Client |
| Client 03 | 10.1.1.12 | Managed Windows Client |
| Client 04 | 10.1.1.13 | Managed Windows Client |

*These are example addresses only. Use addresses appropriate for your network.*

### Server Static IP (Linux - example with netplan)

Edit `/etc/netplan/01-netcfg.yaml`:
```yaml
network:
  version: 2
  ethernets:
    eth0:
      addresses:
        - 10.1.1.1/24
      gateway4: 10.1.1.254
      nameservers:
        addresses:
          - 8.8.8.8
          - 8.8.4.4
```

Apply: `sudo netplan apply`

### Client Static IP (Windows)

1. Open Network Connections (ncpa.cpl)
2. Right-click network adapter → Properties
3. Select Internet Protocol Version 4 (TCP/IPv4) → Properties
4. Use the following IP address:
   - IP address: e.g., 10.1.1.10
   - Subnet mask: 255.255.255.0
   - Default gateway: Your network gateway
   - DNS servers: As appropriate

**Note:** Storing a static IP address in the middleMDM server database does not automatically configure that address on Windows. If actual network configuration is implemented later, it will use supported Windows networking APIs, require explicit administrator authorization, and provide a safe recovery path. Do not silently change network settings.

## Network Discovery

The Network Discovery page in the dashboard shows:
- Registered devices and their reported network information
- Observed IP addresses from client reports
- Reachability status based on heartbeats
- Potential address conflicts

Administrators must explicitly configure which subnets are approved for discovery. Only inspect authorized, configured networks and known assigned addresses. Avoid unrestricted network scanning.

**Important:** Authenticated client heartbeats are the authoritative source of device status. Reachability checks are supplementary.
