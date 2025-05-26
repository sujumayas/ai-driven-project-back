#!/bin/bash

echo "🔧 Rebuilding Docker containers with .env support..."
echo "=================================================="

# Stop existing containers
echo "⏹️  Stopping containers..."
docker-compose down

# Remove old containers and images to ensure clean rebuild
echo "🧹 Cleaning up old containers..."
docker-compose rm -f
docker rmi ai-driven-project-back-api ai-driven-project-back-celery 2>/dev/null || true

# Rebuild with no cache to ensure all changes are applied
echo "🔨 Rebuilding images..."
docker-compose build --no-cache

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services..."
sleep 15

# Check if API is responding
echo "🔍 Testing API endpoints..."
echo ""
echo "1. Health Check:"
curl -s http://localhost:8000/health | python3 -c "import sys, json; print(json.dumps(json.load(sys.stdin), indent=2))" 2>/dev/null || echo "Health check failed"

echo ""
echo "2. Charter Format:"
curl -s http://localhost:8000/api/v1/charter/format | python3 -c "import sys, json; data=json.load(sys.stdin); print('✅ Charter format endpoint working')" 2>/dev/null || echo "❌ Charter format failed"

echo ""
echo "3. AI Status Check:"
curl -s http://localhost:8000/api/v1/charter/status | python3 -c "import sys, json; data=json.load(sys.stdin); print(f'AI Provider: {data.get(\"provider\", \"unknown\")} - Available: {data.get(\"available\", False)}')" 2>/dev/null || echo "❌ AI status check failed"

echo ""
echo "✅ Rebuild complete!"
echo "🌐 API: http://localhost:8000"
echo "📚 Docs: http://localhost:8000/docs"
echo "🔧 Health: http://localhost:8000/health"
echo ""
echo "💡 If you see 'AI Provider not available', that's normal for the first startup."
echo "🔄 Try the validation in the frontend - it should now work with fallback parsing!"
