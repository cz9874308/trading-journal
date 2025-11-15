#!/bin/bash

# Update and deployment script for Vibe Journal
# Run this script on the server to pull latest changes and redeploy

set -e  # Exit on error

echo "=========================================="
echo "Vibe Journal Update & Deployment Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

print_info "Current directory: $SCRIPT_DIR"
echo ""

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    print_error ".env.production file not found!"
    print_info "Please create .env.production with your configuration"
    exit 1
fi

# Load environment variables from .env.production
print_info "Loading environment variables from .env.production..."
export $(grep -v '^#' .env.production | xargs)
print_success "Environment variables loaded"
echo ""

# Show key configuration
print_info "Configuration:"
echo "  API URL: ${NEXT_PUBLIC_API_URL}"
echo "  Database: ${DATABASE_URL}"
echo ""

# Pull latest changes from Git
print_info "Pulling latest changes from Git..."
git pull
print_success "Repository updated"
echo ""

# Stop running containers
print_info "Stopping running containers..."
docker-compose -f docker-compose.prod.yml down
print_success "Containers stopped"
echo ""

# Build containers with environment variables
print_info "Building Docker containers with updated configuration..."
print_info "Building with NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}"
docker-compose -f docker-compose.prod.yml build --no-cache \
    --build-arg NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL}"
print_success "Containers built successfully"
echo ""

# Start containers
print_info "Starting containers..."
docker-compose -f docker-compose.prod.yml up -d
print_success "Containers started"
echo ""

# Wait for services to be ready
print_info "Waiting for services to start (15 seconds)..."
sleep 15
print_success "Services should be ready"
echo ""

# Show container status
print_info "Container status:"
docker-compose -f docker-compose.prod.yml ps
echo ""

# Show recent logs
print_info "Recent logs from frontend:"
docker-compose -f docker-compose.prod.yml logs --tail=20 frontend
echo ""

print_info "Recent logs from backend:"
docker-compose -f docker-compose.prod.yml logs --tail=20 backend
echo ""

echo "=========================================="
print_success "Update and deployment completed!"
echo "=========================================="
echo ""
echo "Your application should now be running at:"
echo "  → ${NEXT_PUBLIC_API_URL%/api}"
echo ""
echo "To view live logs:"
echo "  docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "To restart containers:"
echo "  docker-compose -f docker-compose.prod.yml restart"
echo ""
print_info "Happy trading! 📈"
