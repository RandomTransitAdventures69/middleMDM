# Installation Guide

## Overview

middleMDM consists of a server component (Linux recommended) and client components (Windows). This guide covers the complete installation process.

## Prerequisites

### Server Requirements
- Linux server (Ubuntu 20.04/22.04 recommended) or other Linux distribution
- Python 3.8 or higher
- Public HTTPS access on port 443; keep the Gunicorn backend on loopback port 5001
- For production: PostgreSQL database recommended

### Client Requirements
- Windows 10/11 (Windows-first implementation)
- Python 3.8+ or standalone executable
- Network connectivity to server

## Server Installation

### 1. Clone or Copy the Repository
```bash
cd /opt
# Copy middleMDM files to server
```

### 2. Set up Python Environment
```bash
cd /opt/middleMDM/server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
```

Edit `.env` with your settings:
```bash
SECRET_KEY=
ENROLLMENT_SECRET=
DATABASE_URL=sqlite:///./middlemdm_dev.db  # or PostgreSQL for production
```

Generate each secret separately with:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```
Do not use the example placeholders or reuse the same value for both secrets.

### 4. Initialize Database
```bash
flask --app run init-db
```

This creates the database schema and prompts securely for a new administrator password (at least 12 characters).

### 5. Start the Server

#### Development
```bash
export FLASK_ENV=development
flask --app run
```

#### Production with Gunicorn
```bash
gunicorn -w 4 -b 127.0.0.1:5001 "app:create_app('production')"
```
In production, expose the service only through a trusted HTTPS reverse proxy.

## Client Installation

See [client-setup.md](client-setup.md) for detailed client installation instructions.

## Post-Installation

1. Access the web dashboard over HTTPS through your reverse proxy.
2. Log in as `admin` using the password entered during database initialization.
3. Configure the enrollment secret on authorized clients only.
4. Set up network configuration per [networking.md](networking.md).
