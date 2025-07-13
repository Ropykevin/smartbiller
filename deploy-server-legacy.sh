#!/bin/bash

# SmartBiller Server Deployment Script (Legacy Docker)
# For external server deployment with older docker-compose

set -e  # Exit on any error

echo "🚀 Starting SmartBiller server deployment (Legacy Docker)..."

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

# Stop any existing containers
print_status "Stopping existing containers..."
docker-compose down 2>/dev/null || true

# Remove any existing containers and volumes (clean slate)
print_status "Cleaning up existing containers..."
docker-compose down -v 2>/dev/null || true
docker system prune -f

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p app/static/uploads
mkdir -p app/static/invoices
mkdir -p app/static/receipts

# Set proper permissions
chmod +x run_scheduled_tasks.py

# Check if ports are available
print_status "Checking port availability..."
if lsof -Pi :5020 -sTCP:LISTEN -t >/dev/null ; then
    print_error "Port 5020 is already in use. Please stop the service using this port."
    exit 1
fi

if lsof -Pi :5433 -sTCP:LISTEN -t >/dev/null ; then
    print_error "Port 5433 is already in use. Please stop the service using this port."
    exit 1
fi

# Build and start Docker containers using simplified compose file
print_status "Building and starting Docker containers..."
docker-compose -f docker-compose.server.yml build --no-cache
docker-compose -f docker-compose.server.yml up -d

# Wait for database to be ready
print_status "Waiting for database to be ready..."
sleep 15

# Check if database is accessible
print_status "Checking database connectivity..."
for i in {1..30}; do
    if docker-compose -f docker-compose.server.yml exec db pg_isready -U smartbiller >/dev/null 2>&1; then
        print_status "Database is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Database failed to start within 30 seconds"
        docker-compose -f docker-compose.server.yml logs db
        exit 1
    fi
    sleep 1
done

# Run database migrations
print_status "Running database migrations..."
docker-compose -f docker-compose.server.yml exec web python manage.py db upgrade || {
    print_warning "Database migration failed. This might be normal for first deployment."
}

# Check if services are running
print_status "Checking service status..."
docker-compose -f docker-compose.server.yml ps

# Show logs
print_status "Showing recent logs..."
docker-compose -f docker-compose.server.yml logs --tail=20

print_status "✅ Deployment completed successfully!"
print_status "🌐 Application should be available at: http://localhost:5020"
print_status "🗄️  Database accessible at: localhost:5433"
print_status "📊 To view logs: docker-compose -f docker-compose.server.yml logs -f"
print_status "🛑 To stop: docker-compose -f docker-compose.server.yml down"

# Show container status
echo ""
print_status "Container Status:"
docker-compose -f docker-compose.server.yml ps

# Show port mappings
echo ""
print_status "Port Mappings:"
echo "Web Application: http://localhost:5020"
echo "Database: localhost:5433" 