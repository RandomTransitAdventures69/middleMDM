# middleMDM Client

Cross-platform device agent for Windows, macOS, and Linux.

## Installation

Install Python 3.8+ and the platform dependencies:

```bash
python -m pip install -r requirements.txt
```

## Configuration

Create `config.json` in the platform's configuration directory:

| Platform | Configuration path |
|----------|--------------------|
| Windows | `%PROGRAMDATA%\middleMDM\config.json` |
| macOS | `~/Library/Application Support/middleMDM/config.json` |
| Linux | `${XDG_CONFIG_HOME:-~/.config}/middlemdm/config.json` |

Use your HTTPS server URL and enrollment secret:
```json
{
  "server_url": "https://mdm.example",
  "enrollment_secret": "your-enrollment-secret"
}
```

Use the HTTPS URL from your trusted reverse proxy. TLS certificate verification remains enabled. HTTP is rejected except for explicitly enabled loopback development.

## Usage

Run the agent in the foreground on any supported platform:
```bash
python middlemdm.py
```

On Windows, install the optional service:
```bash
install_service.bat
```

On Linux, use systemd to run the foreground command under a dedicated account. On macOS, use a per-user `launchd` agent. `--service` is Windows-only; the application reports an error if used on other systems.

The client uses native hardware and software inventory sources where available. Linux package inventory supports dpkg, RPM, and pacman; macOS inventory reads installed `.app` bundles.
