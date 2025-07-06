#!/bin/bash

# SmartBiller Deployment Script
# This script handles the complete deployment process

set -e  # Exit on any error

echo "🚀 Starting SmartBiller deployment..."

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

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from template..."
    if [ -f env.example ]; then
        cp env.example .env
        print_status "Created .env file from template. Please update with your actual values."
        print_warning "You need to edit .env file before continuing deployment."
        exit 1
    else
        print_error "env.example not found. Please create .env file manually."
        exit 1
    fi
fi

# Load environment variables
source .env

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p app/static/uploads
mkdir -p app/static/invoices
mkdir -p app/static/receipts

# Set proper permissions
chmod +x run_scheduled_tasks.py

# Pull latest changes
print_status "Pulling latest changes from git..."
git pull origin main || git pull origin master

# Build and start Docker containers
print_status "Building and starting Docker containers..."
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Wait for database to be ready
print_status "Waiting for database to be ready..."
sleep 10

# Run database migrations
print_status "Running database migrations..."
docker-compose exec web python manage.py db upgrade || {
    print_warning "Database migration failed. This might be normal for first deployment."
}

# Setup cron jobs (if not in Docker)
if [ "$SETUP_CRON" = "true" ]; then
    print_status "Setting up cron jobs..."
    bash setup_cron_jobs.sh
fi

# Check if services are running
print_status "Checking service status..."
docker-compose ps

# Show logs
print_status "Showing recent logs..."
docker-compose logs --tail=20

print_status "✅ Deployment completed successfully!"
print_status "🌐 Application should be available at: http://localhost:5020"
print_status "📊 To view logs: docker-compose logs -f"
print_status "🛑 To stop: docker-compose down" 