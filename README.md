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

- **Server**: Python, Flask, SQLAlchemy, SQLite/PostgreSQL; supported on Linux and macOS
- **Client**: Python for Windows, macOS, and Linux
- **API**: RESTful JSON API with authenticated requests
- **Frontend**: HTML, CSS, vanilla JavaScript (no build pipeline required)

## Quick Start

### Server Setup

```bash
cd server
pip install -r requirements.txt
cp .env.example .env  # Set both secrets to separate random values
flask --app run init-db  # Initialize database and set the admin password
FLASK_ENV=development flask --app run  # Local development only
```

Generate two different secrets with `python3 -c "import secrets; print(secrets.token_urlsafe(48))"` and put one each in `SECRET_KEY` and `ENROLLMENT_SECRET` in `.env`. Database initialization securely prompts for the initial administrator password. For local development, set `FLASK_ENV=development` in `.env`; production deployments should use HTTPS through a trusted TLS-terminating reverse proxy.

### Client Setup

See [docs/client-setup.md](docs/client-setup.md) for instructions on enrolling Windows devices.

## Documentation

- [Installation Guide](docs/installation.md) - Complete installation instructions
- [Server Setup](docs/server-setup.md) - Server configuration and deployment
- [Client Setup](docs/client-setup.md) - Client installation and enrollment
- [Networking](docs/networking.md) - Network configuration and IP management
- [Security](docs/security.md) - Security best practices
- [Releases](docs/releases.md) - Build and publish release assets

## Requirements

- Python 3.8+
- Linux or macOS server
- Windows 10/11, macOS, or Linux clients
- Network connectivity between server and clients

## License

See [LICENSE](LICENSE) for details.
