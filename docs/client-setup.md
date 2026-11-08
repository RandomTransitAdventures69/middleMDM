# Client Setup

## Windows Client Installation

### Prerequisites
- Windows 10 or Windows 11
- Python 3.8 or higher installed
- Network connectivity to middleMDM server

### Installation Steps

1. **Copy client files** to the target Windows machine (e.g., `C:\middleMDM\`)

2. **Install dependencies**
```cmd
cd C:\middleMDM\client
pip install -r requirements.txt
```

3. **Configure the client**
Create directory and config file:
```cmd
mkdir "%PROGRAMDATA%\middleMDM"
notepad "%PROGRAMDATA%\middleMDM\config.json"
```

Add configuration:
```json
{
  "server_url": "https://mdm.example",
  "enrollment_secret": "your-enrollment-secret-from-server",
  "heartbeat_interval": 300,
  "inventory_interval": 3600
}
```
Use the HTTPS URL exposed by your trusted reverse proxy and ensure its certificate is trusted by Windows. Requests keep certificate verification enabled. For local development only, `http://localhost:5001` can be enabled by adding `"allow_insecure_http": true`; non-loopback HTTP URLs are rejected.

4. **Test the client**
```cmd
python middlemdm.py
```

The client will automatically enroll and start reporting to the server.

5. **Install as Windows Service** (Recommended for production)
```cmd
cd C:\middleMDM\client
install_service.bat
```

This will install and start the middleMDM Windows service.

### Service Management
```cmd
# Check status
sc query MiddleMDM

# Stop service
net stop MiddleMDM

# Start service
net start MiddleMDM

# Uninstall service
python middlemdm.py --service remove
```

## Troubleshooting

- **Enrollment fails**: Verify enrollment secret matches server configuration
- **Connection issues**: Check firewall rules and server URL
- **Service won't start**: Check Python dependencies and permissions
