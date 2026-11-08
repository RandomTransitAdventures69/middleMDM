# middleMDM Client

Windows client for middleMDM device management platform.

## Installation

1. Install Python 3.8+ on the Windows machine
2. Install dependencies: `pip install -r requirements.txt`
3. Configure the client
4. Install as Windows service or run manually

## Configuration

Create a configuration file at `%PROGRAMDATA%\middleMDM\config.json`:

```json
{
  "server_url": "http://10.1.1.1:5001",
  "enrollment_secret": "your-enrollment-secret"
}
```

## Usage

### Run manually
```bash
python middlemdm.py
```

### Install as Windows service
```bash
install_service.bat
```
