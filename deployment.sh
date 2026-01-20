#!/bin/bash

# SmartBiller Quick Deployment Script
# Minimal deployment script for quick updates

set -e

echo "🚀 Starting SmartBiller quick deployment..."

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin master || git pull origin main

# Run PostgreSQL setup (if needed)
if [ -f mypostgresql.sh ]; then
    echo "🗄️  Setting up PostgreSQL..."
    bash mypostgresql.sh
fi

# Build and start containers
echo "🐳 Building and starting containers..."
docker-compose -f docker-compose.yml up -d --build

# Show logs
echo "📊 Showing container logs..."
docker logs -f smartbiller