# Networking Guide
### boring nerd crap
## Network Requirements

middleMDM requires network connectivity between the server and clients.

### Ports
- Production clients and web interface use HTTPS on TCP 443 through a trusted reverse proxy.
- Gunicorn listens on loopback TCP 5001 by default; do not expose this backend port to clients.
- Local development may use HTTP on TCP 5001.

### Firewall Rules

**Server (Linux):**
```bash
sudo ufw allow 443/tcp
```

**Clients (Windows):**
Allow outbound HTTPS connections to the server on TCP 443. Do not send enrollment secrets or device tokens over remote HTTP.

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
