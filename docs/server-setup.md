# Server Setup

## Configuration

### Environment Variables

| Variable | Required value | Description |
|----------|---------|-------------|
| SECRET_KEY | unique random value, at least 32 characters | Flask secret key for sessions |
| DATABASE_URL | sqlite:///middlemdm_dev.db | Database connection string |
| ENROLLMENT_SECRET | a different unique random value, at least 32 characters | Secret for device enrollment |
| SESSION_COOKIE_SECURE | true in production | Secure session-cookie setting |
| HOST | 127.0.0.1 in production | Server bind address |
| PORT | 5001 | Server port |

Generate each secret separately:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```
Set both values in `server/.env`; never reuse one secret for the other. The application rejects missing, short, or example secrets outside tests. Keep `.env` readable only by the service account.

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

Terminate HTTPS at a trusted reverse proxy and keep Gunicorn bound to loopback. From the server directory:
```bash
cd server
pip install -r requirements.txt
gunicorn -w 4 -b 127.0.0.1:5001 "app:create_app('production')"
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
EnvironmentFile=/opt/middleMDM/server/.env
ExecStart=/opt/middleMDM/server/venv/bin/gunicorn -w 4 -b 127.0.0.1:5001 "app:create_app('production')"
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
sudo ufw allow 443/tcp  # HTTPS reverse proxy
```
