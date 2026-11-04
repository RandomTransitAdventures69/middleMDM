# middleMDM

**An open-source, self-hosted Mobile Device Management platform.**

middleMDM is a project focused on bringing device management back under your control. Instead of relying entirely on expensive cloud-based management platforms, middleMDM aims to provide a self-hosted server for managing, monitoring, and organizing enrolled devices.

Built with schools, small organizations, and homelab environments in mind.

> **Status: In development**
>
> middleMDM is a work in progress. Features and functionality are subject to change. Do not use it to manage production devices yet.

---

## What is middleMDM?

middleMDM is a client-server device management platform.

The server runs on a Linux machine and provides a centralized web interface for administrators. Enrolled devices run a lightweight client that communicates with the server and reports device information.

The goal is simple: one server, multiple clients, and a dashboard to manage everything.

## Planned features

- **Device inventory** — View enrolled devices, hostnames, operating systems, and hardware information.
- **Device monitoring** — Track device status and last check-in time.
- **Network discovery** — Track device IP addresses and identify changes.
- **Static IP management** — Maintain assigned IP addresses for enrolled devices.
- **Software inventory** — See installed software reported by clients.
- **Device groups** — Organize devices by classroom, department, or location.
- **Policy management** — Create and assign configuration policies.
- **Web dashboard** — Manage the environment through a browser.
- **Self-hosted backend** — Keep management infrastructure on your own hardware.

## Architecture

middleMDM uses a client-server architecture.

```text
                 middleMDM SERVER
                 Linux / Flask
                       |
              Web Administration
                       |
                 Device Database
                       |
                REST API / HTTPS
                       |
          +------------+------------+
          |            |            |
       CLIENT 1     CLIENT 2     CLIENT 3
       Windows      Windows      Windows
```

### Server

The server is designed to run on Linux.

Planned technologies:

- Python
- Flask
- SQLite for development
- PostgreSQL for larger deployments
- HTML, CSS, and JavaScript for the dashboard

### Client

The client is designed primarily for Windows endpoints.

Its responsibilities include:

- Registering with the middleMDM server.
- Reporting device information.
- Sending periodic heartbeats.
- Reporting network interfaces and IP addresses.
- Reporting installed software.
- Receiving authorized management policies.

## Network configuration

middleMDM is designed around a network with predictable device addressing.

**Static IP addresses are required for the documented deployment configuration.**

Example:

| Device | Assigned IP |
|---|---|
| middleMDM Server | `10.1.1.1` |
| Client 01 | `10.1.1.10` |
| Client 02 | `10.1.1.11` |
| Client 03 | `10.1.1.12` |

The server should maintain an IP assignment registry associated with each enrolled device.

The system should distinguish between:

- Assigned IP address
- Currently observed IP address
- Last successful check-in
- Network interface information

Static IP configuration must be performed through the operating system's supported network configuration mechanisms. Registering an address in middleMDM does not automatically configure the device.

## Project structure

The intended project structure:

```text
middleMDM/
├── server/
│   ├── app/
│   │   ├── routes/
│   │   ├── models/
│   │   ├── templates/
│   │   └── static/
│   ├── config.py
│   ├── requirements.txt
│   └── run.py
│
├── client/
│   ├── middlemdm/
│   ├── config/
│   └── requirements.txt
│
├── docs/
│   ├── installation.md
│   ├── server-setup.md
│   ├── client-setup.md
│   └── networking.md
│
├── tests/
├── LICENSE
└── README.md
```

This structure may change as development progresses.

## Installation

Installation instructions will be published as the project becomes functional.

The intended deployment model is:

1. Prepare a Linux server.
2. Configure its static IP address.
3. Install the middleMDM server.
4. Configure the database and administrator account.
5. Enroll client devices.
6. Manage enrolled devices through the web dashboard.

See the `docs/` directory for deployment documentation as it becomes available.

## Security

Device management software needs to be treated seriously.

middleMDM is intended to use:

- Authenticated client registration.
- Secure client-server communication over HTTPS.
- Per-device credentials.
- Administrator authentication.
- Role-based access control.
- Audit logging for administrative actions.
- Explicitly authorized management operations.

middleMDM should not provide unrestricted remote shell access or execute arbitrary commands on enrolled devices.

## Compatibility

| Component | Target platform |
|---|---|
| Server | Linux |
| Primary client | Windows |
| Dashboard | Modern web browsers |
| Database | SQLite / PostgreSQL |
| Future clients | macOS / Linux / FreeBSD |

## Development

middleMDM is currently under active development.

Contributions, suggestions, bug reports, and ideas are welcome.

If you find a bug or have a feature request, open an issue on GitHub.

## License

See the `LICENSE` file for licensing information.

---
***middleMDM — Your devices. Your server. Your network.***



**woah time to try a new ai coding agent so uh kilo code do well please**
