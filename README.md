# middleMDM

**Your devices. Your server. Your network.**

middleMDM is an open-source, self-hosted Mobile Device Management (MDM) platform designed primarily for schools, small organizations, and homelab environments. It provides an alternative to cloud-dependent management platforms like Microsoft Intune.

## Features

- **Device Inventory** - Centralized tracking of all enrolled devices with hardware, OS, and network information
- **Device Groups** - Organize devices into groups (Classrooms, Labs, Faculty, etc.)
- **Network Management** - IP assignment registry, network discovery, and conflict detection
- **Software Inventory** - Track installed software across all managed devices
- **Policy Management** - Create and apply policies to device groups or individual devices
- **Authentication & Authorization** - Role-based access control with admin accounts
- **Activity Logging** - Audit trail of all administrative actions
- **Traditional Enterprise UI** - Classic administrative interface inspired by late 1990s-early 2010s IT tools

## Architecture

- **Server**: Python, Flask, SQLAlchemy, SQLite/PostgreSQL
- **Client**: Python for Windows (with future support for macOS, Linux, FreeBSD)
- **API**: RESTful JSON API with authenticated requests
- **Frontend**: HTML, CSS, vanilla JavaScript (no build pipeline required)

## Quick Start

### Server Setup

```bash
cd server
pip install -r requirements.txt
cp .env.example .env  # Edit with your configuration
flask --app run init-db  # Initialize database
flask --app run  # Start development server
```

Default admin credentials: `admin` / `admin123` (change immediately after first login)

### Client Setup

See [docs/client-setup.md](docs/client-setup.md) for instructions on enrolling Windows devices.

## Documentation

- [Installation Guide](docs/installation.md) - Complete installation instructions
- [Server Setup](docs/server-setup.md) - Server configuration and deployment
- [Client Setup](docs/client-setup.md) - Client installation and enrollment
- [Networking](docs/networking.md) - Network configuration and IP management
- [Security](docs/security.md) - Security best practices

## Requirements

- Python 3.8+
- Linux server (primary) or other OS capable of running Flask
- Windows 10/11 for client (Windows-first)
- Network connectivity between server and clients

## License

See [LICENSE](LICENSE) for details.
