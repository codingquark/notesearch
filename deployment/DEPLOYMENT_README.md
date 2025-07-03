# Semantic Search Notes Deployment Guide

This guide will help you deploy your Flask semantic search application with nginx and set up local domain access using **user-level systemd services**.

## Prerequisites

- Ubuntu/Debian Linux system
- Python 3.8+ installed
- Sudo privileges (only for nginx and lingering setup)
- Qdrant vector database running on localhost:6333

## Quick Deployment

1. **Make the deployment script executable and run it:**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

2. **Configure local domain access** (see Router Configuration section below)

3. **Test the deployment:**
   ```bash
   curl http://semantic-search.local/health
   curl 'http://semantic-search.local/search?q=test+query'
   ```

## Manual Deployment Steps

If you prefer to deploy manually or need to troubleshoot:

### 1. Install Dependencies

```bash
# Install nginx if not already installed
sudo apt update
sudo apt install -y nginx

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Set Up User-Level Systemd Service

```bash
# Create user systemd directory
mkdir -p ~/.config/systemd/user

# Copy and update the service file
cp semantic_search.service ~/.config/systemd/user/
sed -i "s|codingquark|$(whoami)|g" ~/.config/systemd/user/semantic_search.service
sed -i "s|/home/codingquark/workspace/semantic_search_notes_v1|$(pwd)|g" ~/.config/systemd/user/semantic_search.service

# Enable lingering (allows user services to run without being logged in)
sudo loginctl enable-linger $(whoami)

# Enable and start the service
systemctl --user daemon-reload
systemctl --user enable semantic_search.service
systemctl --user start semantic_search.service
```

### 3. Configure Nginx

```bash
# Copy nginx configuration
sudo cp semantic_search_nginx.conf /etc/nginx/sites-available/semantic_search

# Enable the site
sudo ln -s /etc/nginx/sites-available/semantic_search /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

## Router Configuration for Local Domain

### Option 1: Router DNS Settings (Recommended)

1. **Access your router's admin panel** (usually http://192.168.1.1 or http://192.168.0.1)

2. **Find DNS settings** (usually under Advanced Settings > DNS or DHCP)

3. **Add a DNS entry:**
   - Hostname: `semantic-search`
   - IP Address: `[YOUR_MACHINE_IP]` (e.g., 192.168.1.100)

4. **Save and restart router if necessary**

### Option 2: Client-side /etc/hosts (Alternative)

On each client machine that needs access, edit `/etc/hosts`:

```bash
# On Linux/Mac
sudo nano /etc/hosts

# On Windows (run as Administrator)
notepad C:\Windows\System32\drivers\etc\hosts
```

Add this line:
```
192.168.1.100 semantic-search.local
```

Replace `192.168.1.100` with your machine's actual IP address.

### Option 3: Local DNS Server (Advanced)

For a more robust solution, you can set up a local DNS server like dnsmasq:

```bash
sudo apt install dnsmasq
sudo nano /etc/dnsmasq.conf
```

Add:
```
address=/semantic-search.local/192.168.1.100
```

## Service Management

### Check Service Status
```bash
# User service (no sudo needed)
systemctl --user status semantic_search.service

# Nginx (requires sudo)
sudo systemctl status nginx
```

### Restart Services
```bash
# User service (no sudo needed)
systemctl --user restart semantic_search.service

# Nginx (requires sudo)
sudo systemctl reload nginx
```

### View Logs
```bash
# Application logs (no sudo needed)
journalctl --user -u semantic_search.service -f

# Nginx access logs (requires sudo)
sudo tail -f /var/log/nginx/semantic_search_access.log

# Nginx error logs (requires sudo)
sudo tail -f /var/log/nginx/semantic_search_error.log
```

### Stop Services
```bash
# User service (no sudo needed)
systemctl --user stop semantic_search.service
systemctl --user disable semantic_search.service

# Nginx (requires sudo)
sudo systemctl stop nginx
```

## Testing the Deployment

### Health Check
```bash
curl http://semantic-search.local/health
```
Expected response: `{"status": "healthy"}`

### Search Test
```bash
curl 'http://semantic-search.local/search?q=your+search+query'
```

### Using a Web Browser
Navigate to: `http://semantic-search.local/health`

## Troubleshooting

### Service Won't Start
1. Check logs: `journalctl --user -u semantic_search.service -n 50`
2. Verify Qdrant is running: `curl http://localhost:6333/collections`
3. Check Python path in service file
4. Verify all dependencies are installed
5. Check if lingering is enabled: `loginctl show-user $(whoami) | grep Linger`

### Nginx Issues
1. Test configuration: `sudo nginx -t`
2. Check error logs: `sudo tail -f /var/log/nginx/error.log`
3. Verify port 80 is not blocked by firewall

### Domain Not Resolving
1. Check router DNS settings
2. Verify IP address is correct
3. Try flushing DNS cache on client machines
4. Test with IP address directly: `curl http://192.168.1.100/health`

### Permission Issues
1. Ensure the service user has access to the workspace directory
2. Check file permissions: `ls -la search_notes.py`
3. Verify Python virtual environment paths
4. Check user systemd directory: `ls -la ~/.config/systemd/user/`

## Advantages of User-Level Services

1. **No sudo required** for service management
2. **Better security** - runs with your user permissions
3. **Easier development** - can start/stop without root access
4. **Cleaner separation** - doesn't clutter system-wide services
5. **Automatic startup** - services start when you log in (with lingering enabled)

## Security Considerations

1. **Firewall**: Configure your firewall to only allow necessary ports
2. **HTTPS**: Consider adding SSL/TLS certificates for production use
3. **Authentication**: Add authentication if the service will be accessible from the internet
4. **Updates**: Keep your system and dependencies updated

## Production Recommendations

For production deployment, consider:

1. **Process Manager**: Use Gunicorn or uWSGI instead of Flask's built-in server
2. **SSL/TLS**: Add HTTPS support with Let's Encrypt certificates
3. **Load Balancing**: Set up multiple instances behind a load balancer
4. **Monitoring**: Add health checks and monitoring (Prometheus, Grafana)
5. **Backup**: Regular backups of your Qdrant database and notes

## API Endpoints

- `GET /health` - Health check
- `GET /search?q=<query>&limit=<number>` - Search notes
- `POST /search` - Search notes with JSON body

Example POST request:
```bash
curl -X POST http://semantic-search.local/search \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "limit": 5}'
``` 