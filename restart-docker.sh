#!/bin/bash

# AI-Driven Project Flow - Docker Restart Script

echo "🐳 Rebuilding and restarting Docker containers..."
echo "================================================"

# Stop existing containers
echo "⏹️  Stopping existing containers..."
docker-compose down

# Rebuild images (in case of new dependencies)
echo "🔨 Rebuilding images..."
docker-compose build --no-cache

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo "🔍 Checking service status..."
echo ""
echo "API Status:"
curl -s http://localhost:8000/health | python -m json.tool 2>/dev/null || echo "API not ready yet"

echo ""
echo "Charter API Status:"
curl -s http://localhost:8000/api/v1/charter/status | python -m json.tool 2>/dev/null || echo "Charter API not ready yet (this is expected without API keys)"

echo ""
echo "✅ Docker restart complete!"
echo "🌐 API: http://localhost:8000"
echo "📚 Docs: http://localhost:8000/docs"
echo "🔧 Health: http://localhost:8000/health"
echo ""
echo "📝 Remember to configure your .env file with AI API keys for full functionality!"
