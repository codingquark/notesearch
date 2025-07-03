#!/bin/bash

# Quick service restart script for semantic search notes

set -e

echo "🔄 Restarting Semantic Search Notes service..."

# Check if service exists
if ! systemctl --user list-unit-files | grep -q semantic_search.service; then
    echo "❌ Service not found. Run deploy_v2.sh first."
    exit 1
fi

# Restart the service
echo "Stopping service..."
systemctl --user stop semantic_search.service || true

echo "Starting service..."
systemctl --user start semantic_search.service

# Wait a moment and check status
sleep 3

if systemctl --user is-active --quiet semantic_search.service; then
    echo "✅ Service restarted successfully"
    
    # Test health endpoint
    if curl -s http://localhost:5000/health > /dev/null; then
        echo "✅ Health check passed"
    else
        echo "⚠️  Health check failed (service may still be starting)"
    fi
else
    echo "❌ Service failed to start"
    echo ""
    echo "Service status:"
    systemctl --user status semantic_search.service --no-pager
    exit 1
fi

echo ""
echo "Service logs (last 10 lines):"
journalctl --user -u semantic_search.service --no-pager -n 10