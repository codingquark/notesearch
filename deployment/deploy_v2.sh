#!/bin/bash

# Semantic Search Notes Deployment Script (Version 2)
# This script sets up the new packaged version with CLI commands

set -e  # Exit on any error

echo "🚀 Starting Semantic Search Notes deployment (v2.0)..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Get current user and workspace
CURRENT_USER=$(whoami)
WORKSPACE_DIR=$(pwd)
USER_SYSTEMD_DIR="$HOME/.config/systemd/user"

print_status "Deploying for user: $CURRENT_USER"
print_status "Workspace directory: $WORKSPACE_DIR"

# Check if we're in the right directory
if [[ ! -f "pyproject.toml" ]] || [[ ! -d "src/semantic_notes" ]]; then
    print_error "This doesn't appear to be the semantic_notes project root directory"
    print_error "Please run this script from the project root where pyproject.toml exists"
    exit 1
fi

# Check Python version
print_step "Checking Python version..."
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")

# Parse version numbers for comparison
MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

# Check if version is 3.9 or higher
if [[ $MAJOR -lt 3 ]] || [[ $MAJOR -eq 3 && $MINOR -lt 9 ]]; then
    print_error "Python 3.9 or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi
print_status "Python version: $PYTHON_VERSION ✓"

# Install the package
print_step "Installing semantic_notes package..."
if [[ -d ".direnv" ]]; then
    print_status "Found direnv environment, using it"
    source .envrc 2>/dev/null || true
    pip install -e .
else
    print_status "Installing with system Python"
    pip install -e . --user
fi
print_status "Package installed ✓"

# Check if Qdrant is running
print_step "Checking Qdrant connection..."
if curl -s http://localhost:6333/collections > /dev/null 2>&1; then
    print_status "Qdrant is running ✓"
else
    print_warning "Qdrant not accessible at localhost:6333"
    print_warning "Make sure Qdrant is running before starting the service"
fi

# Test CLI commands
print_step "Testing CLI commands..."
if command -v semantic-notes-serve &> /dev/null; then
    print_status "CLI commands available ✓"
else
    print_error "CLI commands not found. Package installation may have failed."
    exit 1
fi

# Create and update systemd service
print_step "Setting up systemd service..."
mkdir -p "$USER_SYSTEMD_DIR"

# Create updated service file
cat > "$USER_SYSTEMD_DIR/semantic_search.service" << EOF
[Unit]
Description=Semantic Search Notes Flask Application
After=network.target

[Service]
Type=simple
WorkingDirectory=$WORKSPACE_DIR
Environment=PATH=$PATH
Environment=PYTHONPATH=$WORKSPACE_DIR/src
ExecStart=$(which semantic-notes-serve) --host 127.0.0.1 --port 5000
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
EOF

print_status "Systemd service file created ✓"

# Reload and enable service
systemctl --user daemon-reload
systemctl --user enable semantic_search.service
print_status "Systemd service enabled ✓"

# Enable lingering for the user
print_step "Enabling user service lingering..."
sudo loginctl enable-linger "$CURRENT_USER"
print_status "User lingering enabled ✓"

# Check if nginx is installed
print_step "Setting up nginx..."
if ! command -v nginx &> /dev/null; then
    print_status "Installing nginx..."
    sudo apt update
    sudo apt install -y nginx
fi

# Configure nginx
sudo cp deployment/semantic_search_nginx.conf /etc/nginx/sites-available/semantic_search

# Create symbolic link to enable the site
if [[ -L "/etc/nginx/sites-enabled/semantic_search" ]]; then
    sudo rm /etc/nginx/sites-enabled/semantic_search
fi
sudo ln -s /etc/nginx/sites-available/semantic_search /etc/nginx/sites-enabled/

# Test nginx configuration
if sudo nginx -t; then
    print_status "Nginx configuration is valid ✓"
else
    print_error "Nginx configuration is invalid"
    exit 1
fi

# Start services
print_step "Starting services..."
systemctl --user start semantic_search.service
sudo systemctl reload nginx

# Check service status
print_step "Checking service status..."
sleep 3  # Give services time to start

if systemctl --user is-active --quiet semantic_search.service; then
    print_status "✅ Semantic Search service is running"
else
    print_error "❌ Semantic Search service failed to start"
    echo ""
    echo "Service logs:"
    systemctl --user status semantic_search.service --no-pager
    echo ""
    echo "Recent journal entries:"
    journalctl --user -u semantic_search.service --no-pager -n 20
    exit 1
fi

if sudo systemctl is-active --quiet nginx; then
    print_status "✅ Nginx is running"
else
    print_error "❌ Nginx failed to start"
    sudo systemctl status nginx
    exit 1
fi

# Test the API endpoints
print_step "Testing API endpoints..."
sleep 2  # Give the service a moment to fully start

if curl -s http://localhost:5000/health > /dev/null; then
    print_status "✅ Health endpoint responding"
else
    print_warning "⚠️  Health endpoint not responding (service may still be starting)"
fi

# Get machine IP address
MACHINE_IP=$(hostname -I | awk '{print $1}')
print_status "Machine IP address: $MACHINE_IP"

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Service Information:"
echo "   • Package: semantic-notes v$(python3 -c 'import semantic_notes; print(semantic_notes.__version__)')"
echo "   • Service: semantic_search.service (user-level)"
echo "   • Web server: nginx (proxy to localhost:5000)"
echo ""
echo "🔧 Management Commands:"
echo "   • Start service:    systemctl --user start semantic_search.service"
echo "   • Stop service:     systemctl --user stop semantic_search.service"
echo "   • Restart service:  systemctl --user restart semantic_search.service"
echo "   • Service status:   systemctl --user status semantic_search.service"
echo "   • View logs:        journalctl --user -u semantic_search.service -f"
echo ""
echo "🌐 API Endpoints:"
echo "   • Health check:     curl http://localhost:5000/health"
echo "   • System info:      curl http://localhost:5000/info"
echo "   • Search:           curl 'http://localhost:5000/search?q=your+query'"
echo ""
echo "🏠 Local Access:"
echo "   • Direct:           http://localhost:5000"
echo "   • Through nginx:    http://semantic-search.gluon.lan"
echo ""
echo "📝 Next Steps:"
echo "1. Index your notes:"
echo "   semantic-notes-index --notes-dir ./notes"
echo ""
echo "2. Add DNS entry for external access:"
echo "   $MACHINE_IP semantic-search.gluon.lan"
echo ""
echo "3. Test the service:"
echo "   curl http://semantic-search.gluon.lan/health"
echo "   curl 'http://semantic-search.gluon.lan/search?q=productivity'"
echo ""