#!/bin/bash

echo "🔧 Quick Docker rebuild with configuration fixes..."
echo "================================================="

# Stop containers
echo "⏹️  Stopping containers..."
docker-compose down

# Rebuild only the API container
echo "🔨 Rebuilding API container..."
docker-compose build api

# Start only the essential services for testing
echo "🚀 Starting essential services..."
docker-compose up -d db redis
sleep 5

# Test the configuration inside the container
echo "🧪 Testing configuration..."
docker-compose run --rm api python /app/test_config.py

# If config test passes, start the API
if [ $? -eq 0 ]; then
    echo "✅ Configuration test passed! Starting API..."
    docker-compose up -d api
    sleep 10
    
    echo "🔍 Testing API endpoints..."
    curl -s http://localhost:8000/health | python3 -c "import sys, json; print('Health:', json.loads(sys.stdin.read()))" 2>/dev/null || echo "❌ Health check failed"
    
    echo "🎯 Testing charter endpoint..."
    curl -s -X POST http://localhost:8000/api/v1/charter/debug-validate \
      -H "Content-Type: application/json" \
      -d '{"charter_text": "test charter"}' | python3 -c "import sys, json; print('Debug:', json.loads(sys.stdin.read())['message'])" 2>/dev/null || echo "❌ Charter endpoint failed"
else
    echo "❌ Configuration test failed. Check the logs above."
fi

echo "✅ Quick rebuild complete!"
