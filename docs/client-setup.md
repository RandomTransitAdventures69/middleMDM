# Client Setup

The middleMDM client runs on Windows, macOS, and Linux. It can run in a terminal on all three platforms; the Windows service wrapper is available only on Windows.

## Install

Install Python 3.8+ and client dependencies from the repository root:

```bash
cd client
python -m pip install -r requirements.txt
```

Windows-only WMI and service packages install automatically on Windows; macOS and Linux install only the portable dependencies.

## Configure

Create `config.json` at:

| Platform | Configuration path |
|----------|--------------------|
| Windows | `%PROGRAMDATA%\middleMDM\config.json` |
| macOS | `~/Library/Application Support/middleMDM/config.json` |
| Linux | `${XDG_CONFIG_HOME:-~/.config}/middlemdm/config.json` |

Example:

```json
{
  "server_url": "https://freetvnopaywallnoscamnoviruses.nopriating",
  "enrollment_secret": "hehehskaurueueiajajhdh72737363$/$nsbria",
  "heartbeat_interval": 300,
  "inventory_interval": 1
}
```

Use the HTTPS hostname served by your trusted reverse proxy and a certificate trusted by the operating system. TLS verification remains enabled. Remote HTTP URLs are rejected. For local development only, `http://localhost:5001` may be enabled with `"allow_insecure_http": true`.

The client creates its configuration directory when saving its generated device ID and API token. On macOS and Linux, it restricts that directory to the current account.

## Run interactively

From the client directory:

```bash
python middlemdm.py
```

The agent enrolls the device, sends periodic heartbeats, and reports inventory. Stop it with Ctrl+C.

## Run as a service

### Windows

Run the included installer from an elevated command prompt:

```cmd
install_service.bat
```

The Windows service can also be managed with `sc query MiddleMDM`, `net stop MiddleMDM`, and `net start MiddleMDM`.

### Linux (systemd)

Run the client under a dedicated service account and install a unit such as `/etc/systemd/system/middlemdm-agent.service`:

```ini
[Unit]
Description=middleMDM Device Agent
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=middlemdm
Environment=HOME=/var/lib/middlemdm
WorkingDirectory=/opt/middleMDM/client
ExecStart=/opt/middleMDM/venv/bin/python /opt/middleMDM/client/middlemdm.py
Restart=on-failure
RestartSec=15

[Install]
WantedBy=multi-user.target
```

Create the config at `/var/lib/middlemdm/.config/middlemdm/config.json`, then enable the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now middlemdm-agent
```

### macOS (launchd)

Run the agent as the user whose configuration contains the enrollment secret. Create `~/Library/LaunchAgents/com.middlemdm.agent.plist`, replacing the Python and client paths:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.middlemdm.agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/middleMDM/client/middlemdm.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Load it for the current user:

```bash
launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.middlemdm.agent.plist"
```

## Troubleshooting

- **Enrollment fails:** Verify the server URL, TLS certificate, and enrollment secret.
- **Connection issues:** Confirm the server's HTTPS reverse proxy is reachable.
- **Inventory is incomplete:** Some hardware fields are unavailable on certain operating systems or require elevated permissions.
