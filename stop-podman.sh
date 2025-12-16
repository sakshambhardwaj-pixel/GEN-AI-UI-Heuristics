#!/bin/bash

# Stop Script for GEN-AI-UI-Heuristics Podman Deployment

set -e

echo "🛑 Stopping GEN-AI-UI-Heuristics Podman Deployment"
echo "=================================================="

# Configuration
POD_NAME="heuristic-evaluation-pod"
CONTAINER_NAME="heuristic-evaluation-app"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Stop the pod and containers
print_status "Stopping Podman pod and containers..."

# Stop using kube yaml (recommended)
if [ -f "podman-compose.yml" ]; then
    print_status "Stopping using Podman Kube YAML..."
    podman play kube --down podman-compose.yml 2>/dev/null || {
        print_warning "Failed to stop using kube yaml, trying manual cleanup..."
    }
fi

# Manual cleanup as fallback
print_status "Performing manual cleanup..."
podman pod stop $POD_NAME 2>/dev/null || print_warning "Pod $POD_NAME not found or already stopped"
podman pod rm $POD_NAME 2>/dev/null || print_warning "Pod $POD_NAME not found or already removed"
podman container stop $CONTAINER_NAME 2>/dev/null || print_warning "Container $CONTAINER_NAME not found or already stopped"
podman container rm $CONTAINER_NAME 2>/dev/null || print_warning "Container $CONTAINER_NAME not found or already removed"

print_success "✅ Application stopped successfully!"

# Show remaining containers/pods (for verification)
print_status "Checking for any remaining related containers..."
REMAINING=$(podman ps -a --filter "name=$CONTAINER_NAME" --format "table {{.Names}}" | grep -v NAMES || true)
if [ -n "$REMAINING" ]; then
    print_warning "Found remaining containers: $REMAINING"
else
    print_success "No remaining containers found"
fi

echo ""
print_success "🎉 Cleanup completed successfully!"
print_status "To restart the application, run: ./build-podman.sh"
