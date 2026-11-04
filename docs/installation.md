# Installation Guide

## Overview

middleMDM consists of a server component (Linux recommended) and client components (Windows). This guide covers the complete installation process.

## Prerequisites

### Server Requirements
- Linux server (Ubuntu 20.04/22.04 recommended) or other Linux distribution
- Python 3.8 or higher
- Network access on port 5000 (or as configured)
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
SECRET_KEY=your-random-secret-key-here
ENROLLMENT_SECRET=your-device-enrollment-secret-here
DATABASE_URL=sqlite:///./middlemdm_dev.db  # or PostgreSQL for production
```

### 4. Initialize Database
```bash
flask --app run init-db
```

This creates the database schema and default admin user (admin/admin123).

### 5. Start the Server

#### Development
```bash
flask --app run
```

#### Production with Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

## Client Installation

See [client-setup.md](client-setup.md) for detailed client installation instructions.

## Post-Installation

1. Access the web dashboard at `http://your-server:5000`
2. Log in with default credentials (admin/admin123)
3. **Change the default password immediately**
4. Configure enrollment secret
5. Set up network configuration per [networking.md](networking.md)
