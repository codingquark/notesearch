#!/bin/bash

# Semantic Search Notes Deployment Script
# This script sets up the Flask application as a user-level systemd service with nginx reverse proxy

set -e  # Exit on any error

echo "🚀 Starting Semantic Search Notes deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Get current user and workspace
CURRENT_USER=$(whoami)
WORKSPACE_DIR=$(pwd)
USER_SYSTEMD_DIR="$HOME/.config/systemd/user"

print_status "Deploying for user: $CURRENT_USER"
print_status "Workspace directory: $WORKSPACE_DIR"
print_status "User systemd directory: $USER_SYSTEMD_DIR"

# Check if required files exist
if [[ ! -f "src/semantic_notes/__init__.py" ]]; then
    print_error "semantic_notes package not found. Make sure you're in the project root directory."
    exit 1
fi

if [[ ! -f "deployment/semantic_search.service" ]]; then
    print_error "deployment/semantic_search.service not found"
    exit 1
fi

if [[ ! -f "deployment/semantic_search_nginx.conf" ]]; then
    print_error "deployment/semantic_search_nginx.conf not found"
    exit 1
fi

if [[ ! -f "pyproject.toml" ]]; then
    print_error "pyproject.toml not found. This doesn't appear to be a properly structured project."
    exit 1
fi

# Update service file with correct paths
print_status "Updating systemd service file..."
cp deployment/semantic_search.service /tmp/semantic_search.service.tmp
sed -i "s|codingquark|$CURRENT_USER|g" /tmp/semantic_search.service.tmp
sed -i "s|/home/codingquark/workspace/semantic_search_notes_v1|$WORKSPACE_DIR|g" /tmp/semantic_search.service.tmp

# Check if Python virtual environment exists
if [[ -d ".direnv" ]]; then
    print_status "Found direnv environment, using it"
    PYTHON_PATH="$WORKSPACE_DIR/.direnv/python-3.12.2/bin/python"
    if [[ ! -f "$PYTHON_PATH" ]]; then
        print_warning "Python not found in .direnv, will use system Python"
        PYTHON_PATH="python3"
    fi
else
    print_warning "No .direnv found, using system Python"
    PYTHON_PATH="python3"
fi

# Install the package first
print_status "Installing semantic_notes package..."
if [[ -d ".direnv" ]]; then
    # Use direnv environment
    source .envrc 2>/dev/null || true
    pip install -e .
else
    # Use system Python
    pip install -e . --user
fi

# Update service file with correct gunicorn command
# The service file already has the correct ExecStart command for the new structure

# Create user systemd directory if it doesn't exist
print_status "Setting up user systemd service..."
mkdir -p "$USER_SYSTEMD_DIR"

# Install user-level systemd service
print_status "Installing user systemd service..."
cp /tmp/semantic_search.service.tmp "$USER_SYSTEMD_DIR/semantic_search.service"
systemctl --user daemon-reload
systemctl --user enable semantic_search.service

# Enable lingering for the user (allows user services to run without being logged in)
print_status "Enabling user service lingering..."
sudo loginctl enable-linger "$CURRENT_USER"

# Check if nginx is installed
if ! command -v nginx &> /dev/null; then
    print_status "Installing nginx..."
    sudo apt update
    sudo apt install -y nginx
fi

# Configure nginx
print_status "Configuring nginx..."
sudo cp deployment/semantic_search_nginx.conf /etc/nginx/sites-available/semantic_search

# Create symbolic link to enable the site
if [[ -L "/etc/nginx/sites-enabled/semantic_search" ]]; then
    sudo rm /etc/nginx/sites-enabled/semantic_search
fi
sudo ln -s /etc/nginx/sites-available/semantic_search /etc/nginx/sites-enabled/

# Test nginx configuration
print_status "Testing nginx configuration..."
if sudo nginx -t; then
    print_status "Nginx configuration is valid"
else
    print_error "Nginx configuration is invalid"
    exit 1
fi

# Start services
print_status "Starting services..."
systemctl --user start semantic_search.service
sudo systemctl reload nginx

# Check service status
print_status "Checking service status..."
if systemctl --user is-active --quiet semantic_search.service; then
    print_status "✅ Semantic Search service is running"
else
    print_error "❌ Semantic Search service failed to start"
    systemctl --user status semantic_search.service
    exit 1
fi

if sudo systemctl is-active --quiet nginx; then
    print_status "✅ Nginx is running"
else
    print_error "❌ Nginx failed to start"
    sudo systemctl status nginx
    exit 1
fi

# Get machine IP address
MACHINE_IP=$(hostname -I | awk '{print $1}')
print_status "Machine IP address: $MACHINE_IP"

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Add this line to your router's DNS settings or /etc/hosts on client machines:"
echo "   $MACHINE_IP semantic-search.local"
echo ""
echo "2. Test the service:"
echo "   curl http://semantic-search.local/health"
echo "   curl http://semantic-search.local/info"
echo "   curl 'http://semantic-search.local/search?q=your+search+query'"
echo ""
echo "3. User service management commands (no sudo needed):"
echo "   systemctl --user status semantic_search.service"
echo "   systemctl --user restart semantic_search.service"
echo "   systemctl --user stop semantic_search.service"
echo "   systemctl --user enable semantic_search.service"
echo "   systemctl --user disable semantic_search.service"
echo ""
echo "4. View logs:"
echo "   journalctl --user -u semantic_search.service -f"
echo "   sudo tail -f /var/log/nginx/semantic_search_access.log"
echo "" 