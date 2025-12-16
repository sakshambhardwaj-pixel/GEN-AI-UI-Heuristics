#!/bin/bash

# Build and Deploy Script for GEN-AI-UI-Heuristics with Podman
# This script builds the container image and runs it using Podman

set -e

echo "🚀 Building and Deploying GEN-AI-UI-Heuristics with Podman"
echo "============================================================"

# Configuration
IMAGE_NAME="localhost/heuristic-evaluation:latest"
CONTAINER_NAME="heuristic-evaluation-app"
POD_NAME="heuristic-evaluation-pod"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
if [ ! -f "GEN-AI-Heuristics/.env" ]; then
    print_warning ".env file not found in GEN-AI-Heuristics directory"
    print_warning "Creating template .env file - please update with your OpenAI API key"
    cat > GEN-AI-Heuristics/.env << EOF
# OpenAI API Key - Required for heuristic evaluation
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Additional environment variables
# STREAMLIT_THEME_BASE=light
# STREAMLIT_THEME_PRIMARY_COLOR=#ff6b35
EOF
    print_warning "Please edit GEN-AI-Heuristics/.env and add your OpenAI API key before continuing"
    read -p "Press Enter to continue once you've updated the .env file..."
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p uploads data

# Clean up any existing containers/pods
print_status "Cleaning up existing containers..."
podman pod rm -f $POD_NAME 2>/dev/null || true
podman container rm -f $CONTAINER_NAME 2>/dev/null || true

# Build the image
print_status "Building Docker image with Podman..."
podman build -f Dockerfile.podman -t $IMAGE_NAME .

if [ $? -eq 0 ]; then
    print_success "Image built successfully: $IMAGE_NAME"
else
    print_error "Failed to build image"
    exit 1
fi

# Load environment variables
if [ -f "GEN-AI-Heuristics/.env" ]; then
    export $(cat GEN-AI-Heuristics/.env | grep -v '^#' | xargs)
fi

# Validate OpenAI API key
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
    print_error "OpenAI API key is not set or still has default value"
    print_error "Please update the OPENAI_API_KEY in GEN-AI-Heuristics/.env file"
    exit 1
fi

# Run with Podman using the YAML file
print_status "Starting application with Podman Kube..."
OPENAI_API_KEY=$OPENAI_API_KEY podman play kube podman-compose.yml

if [ $? -eq 0 ]; then
    print_success "Application started successfully!"
    echo ""
    print_success "🌐 Access your application at: http://localhost:8501"
    echo ""
    print_status "Container logs: podman logs $CONTAINER_NAME"
    print_status "Stop application: podman pod stop $POD_NAME"
    print_status "Remove application: podman pod rm $POD_NAME"
    echo ""
    print_status "Waiting for application to be ready..."
    
    # Wait for health check
    for i in {1..30}; do
        if curl -f http://localhost:8501/_stcore/health >/dev/null 2>&1; then
            print_success "✅ Application is ready and healthy!"
            break
        fi
        echo -n "."
        sleep 2
    done
    
    if [ $i -eq 30 ]; then
        print_warning "Health check timeout - application may still be starting"
        print_status "Check logs with: podman logs $CONTAINER_NAME"
    fi
    
else
    print_error "Failed to start application"
    exit 1
fi

echo ""
print_success "🎉 Deployment completed successfully!"
print_status "Your Streamlit Heuristic Evaluation app is running at http://localhost:8501"
