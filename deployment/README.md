# Deployment Guide

This directory contains deployment configurations and scripts for the Semantic Search Notes application.

## Files Overview

- `deploy_v2.sh` - **New deployment script** for the restructured package
- `deploy.sh` - Legacy deployment script (for reference)
- `restart_service.sh` - Quick service restart utility
- `semantic_search.service` - Systemd service configuration
- `semantic_search_nginx.conf` - Nginx reverse proxy configuration
- `gunicorn.conf.py` - Gunicorn WSGI server configuration

## Quick Deployment

### 1. Prerequisites

- Python 3.9 or higher
- Qdrant running on localhost:6333
- Nginx (will be installed if not present)
- Sudo access for nginx configuration

### 2. Deploy the Service

```bash
# From the project root directory
cd /path/to/semantic_search_notes_v1
./deployment/deploy_v2.sh
```

This script will:
- Install the semantic_notes package
- Create systemd user service
- Configure nginx reverse proxy
- Start all services
- Perform health checks

### 3. Index Your Notes

```bash
semantic-notes-index --notes-dir ./notes
```

### 4. Test the Service

```bash
# Health check
curl http://localhost:5000/health

# System info
curl http://localhost:5000/info

# Search test
curl 'http://localhost:5000/search?q=productivity&limit=5'
```

## Service Management

### User Systemd Service Commands

```bash
# Start service
systemctl --user start semantic_search.service

# Stop service
systemctl --user stop semantic_search.service

# Restart service
systemctl --user restart semantic_search.service
# OR use the convenience script:
./deployment/restart_service.sh

# Check status
systemctl --user status semantic_search.service

# View logs
journalctl --user -u semantic_search.service -f

# Enable/disable auto-start
systemctl --user enable semantic_search.service
systemctl --user disable semantic_search.service
```

### Nginx Commands

```bash
# Test configuration
sudo nginx -t

# Reload configuration
sudo systemctl reload nginx

# Restart nginx
sudo systemctl restart nginx

# Check status
sudo systemctl status nginx
```

## Configuration

### Environment Variables

The service can be configured via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `NOTES_DIR` | `./notes` | Directory containing notes |
| `QDRANT_HOST` | `localhost` | Qdrant server host |
| `QDRANT_PORT` | `6333` | Qdrant server port |
| `MODEL_NAME` | `all-mpnet-base-v2` | Sentence transformer model |
| `FLASK_HOST` | `localhost` | API server bind host |
| `FLASK_PORT` | `5000` | API server bind port |

Add environment variables to the systemd service file:

```ini
[Service]
Environment=NOTES_DIR=/path/to/your/notes
Environment=MODEL_NAME=all-MiniLM-L6-v2
```

### Service Configuration

The systemd service is installed as a **user service**, meaning:
- No sudo required for management
- Runs under your user account
- Automatically starts on boot (with lingering enabled)
- Isolated from system services

### Nginx Configuration

The nginx configuration provides:
- Reverse proxy to localhost:5000
- Security headers
- Increased timeouts for search operations
- Separate endpoints for health, info, and search
- Access and error logging

## Network Access

### Local Access
- Direct API: `http://localhost:5000`
- Through nginx: `http://semantic-search.gluon.lan` (requires DNS)

### External Access

Add to your router's DNS or client `/etc/hosts`:
```
<server-ip> semantic-search.gluon.lan
```

## Troubleshooting

### Common Issues

1. **Service won't start**
   ```bash
   # Check logs
   journalctl --user -u semantic_search.service -n 50
   
   # Check if package is installed
   pip list | grep semantic-notes
   
   # Reinstall package
   pip install -e .
   ```

2. **Qdrant connection errors**
   ```bash
   # Check if Qdrant is running
   curl http://localhost:6333/collections
   
   # Start Qdrant (if using Docker)
   docker run -p 6333:6333 qdrant/qdrant
   ```

3. **Nginx configuration errors**
   ```bash
   # Test nginx config
   sudo nginx -t
   
   # Check if port 80 is available
   sudo netstat -tlnp | grep :80
   ```

4. **Permission issues**
   ```bash
   # Check user lingering
   loginctl show-user $USER | grep Linger
   
   # Enable if needed
   sudo loginctl enable-linger $USER
   ```

### Log Locations

- **Service logs**: `journalctl --user -u semantic_search.service`
- **Nginx access**: `/var/log/nginx/semantic_search_access.log`
- **Nginx errors**: `/var/log/nginx/semantic_search_error.log`

### Performance Tuning

1. **Memory usage**: Consider using smaller models for lower memory usage
2. **CPU usage**: Adjust Gunicorn workers in `gunicorn.conf.py`
3. **Search timeout**: Increase nginx timeout for large note collections

## Updating the Service

When you update the code:

1. Reinstall the package:
   ```bash
   pip install -e .
   ```

2. Restart the service:
   ```bash
   ./deployment/restart_service.sh
   ```

## Migration from Old Structure

If you had the old deployment running:

1. Stop the old service:
   ```bash
   systemctl --user stop semantic_search.service
   ```

2. Run the new deployment:
   ```bash
   ./deployment/deploy_v2.sh
   ```

The new deployment will overwrite the old service configuration.

## Security Considerations

- Service runs as unprivileged user
- No sudo required for service management
- Security headers configured in nginx
- API only accessible via localhost by default
- Consider adding HTTPS/TLS for external access

## Advanced Configuration

### Custom Gunicorn Settings

Edit `deployment/gunicorn.conf.py` for custom WSGI server settings:
- Worker count
- Timeout values
- Logging configuration
- Memory limits

### Custom Nginx Settings

Edit `deployment/semantic_search_nginx.conf` for:
- Custom domains
- SSL/TLS configuration
- Rate limiting
- Additional security headers