# Server Setup

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| SECRET_KEY | change-me-in-production | Flask secret key for sessions |
| DATABASE_URL | sqlite:///middlemdm_dev.db | Database connection string |
| ENROLLMENT_SECRET | dev-enrollment-secret-change-me | Secret for device enrollment |
| SESSION_COOKIE_SECURE | false | Set to true for HTTPS |
| HOST | 0.0.0.0 | Server bind address |
| PORT | 5001 | Server port |

### Database Setup

#### SQLite (Development/Small Deployments)
Default configuration uses SQLite. No additional setup required.

#### PostgreSQL (Production)
```bash
sudo apt install postgresql postgresql-contrib
sudo -u postgres createuser middlemdm
sudo -u postgres createdb middlemdm
sudo -u postgres psql -c "ALTER USER middlemdm PASSWORD 'password';"
```

Update DATABASE_URL in .env:
```
DATABASE_URL=postgresql://middlemdm:password@localhost/middlemdm
```

## Deployment with Gunicorn

For production, use Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 "server.app:create_app()"
```

Or from the server directory:
```bash
cd server
gunicorn -w 4 -b 0.0.0.0:5001 "app:create_app()"
```

## Systemd Service (Linux)

Create `/etc/systemd/system/middlemdm.service`:
```ini
[Unit]
Description=middleMDM Server
After=network.target

[Service]
User=middlemdm
Group=middlemdm
WorkingDirectory=/opt/middleMDM/server
Environment=PATH=/opt/middleMDM/server/venv/bin
ExecStart=/opt/middleMDM/server/venv/bin/gunicorn -w 4 -b 0.0.0.0:5001 "app:create_app()"
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable middlemdm
sudo systemctl start middlemdm
```

## Firewall Configuration

Allow traffic on the configured port:
```bash
sudo ufw allow 5000/tcp
```
