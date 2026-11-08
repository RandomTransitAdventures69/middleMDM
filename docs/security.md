# Security Guide

## Security Principles

- **Your devices. Your server. Your network.** - Self-hosted for full control
- **Authentication required** - All admin access and API calls must be authenticated
- **Least privilege** - Role-based access control
- **No arbitrary remote execution** - Unrestricted command execution is not implemented
- **Audit logging** - All administrative actions are logged

## Authentication

### Administrator Authentication
- Secure password hashing using Werkzeug
- The initial administrator password is entered interactively during database setup; no shared default password is used
- Session management with secure cookies
- CSRF protection on forms
- Role-based permissions

### Device Authentication
- Each device receives a unique API token during enrollment
- Tokens are used for all device API calls (heartbeats, inventory, etc.)
- Device credentials are never exposed in the dashboard

## Best Practices

### Server Security
1. **Use separate strong secrets** - Set random `SECRET_KEY` and `ENROLLMENT_SECRET` values of at least 32 characters
2. **Use HTTPS in production** - Terminate TLS at a trusted reverse proxy; keep Gunicorn on loopback
3. **Protect configuration files** - Restrict `.env` to the server service account
4. **Keep software updated** - Update dependencies regularly
5. **Restrict network access** - Use firewall rules to limit access
6. **Use PostgreSQL in production** - SQLite is for development only
7. **Regular backups** - Back up database regularly

### Client Security
1. **Protect enrollment secret** - Only share with authorized devices
2. **Use HTTPS** - Client requests verify the server certificate; remote HTTP URLs are rejected
3. **Run as service with appropriate permissions** - Follow least privilege principle
4. **Keep client updated** - Deploy updates through controlled process

### Network Security
1. **Use static IPs as documented** - Configure proper network addressing
2. **Segment management traffic** - Consider separate management VLAN if possible
3. **Monitor logs** - Review activity logs regularly
4. **Detect conflicts** - Monitor for duplicate IP addresses

## Secret Management

- Never hardcode passwords, API keys, or secret tokens
- Use environment variables for all secrets
- Store secrets securely in production environments
- Rotate secrets periodically

## API Security

- All API endpoints (except enrollment with valid secret) require authentication
- Device API uses bearer tokens
- Admin API uses session authentication
- Input validation on all requests
- No unrestricted remote shell execution

## Audit Logging

All significant events are logged to the EventLog including:
- Authentication attempts (success/failure)
- Device enrollment
- Policy changes
- Administrative actions
- API access
