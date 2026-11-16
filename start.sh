#!/bin/bash
# MiniRack Management Portal - Quick Start Script
set -e

echo "🚀 MiniRack Management Portal - Quick Start"
echo "============================================"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from example..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your settings"
fi

# Build and start
echo "🔨 Building Docker image..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Wait for service to be ready
echo "⏳ Waiting for service to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8080/health > /dev/null; then
        echo "✅ Service is ready!"
        break
    fi
    echo "  Attempt $i/30..."
    sleep 1
done

echo ""
echo "✅ Deployment Complete!"
echo "==============================================="
echo "🌐 Portal URL: http://localhost:8080"
echo "📚 API Docs: http://localhost:8080/api/docs"
echo ""
echo "Available endpoints:"
echo "  - Dashboard: http://localhost:8080"
echo "  - Health: http://localhost:8080/health"
echo "  - API: http://localhost:8080/api/v1"
echo ""
echo "View logs with: docker-compose logs -f"
echo "Stop services: docker-compose down"
echo "==============================================="
