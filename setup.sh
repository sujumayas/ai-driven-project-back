#!/bin/bash

# AI-Driven Project Flow - Quick Setup Script
# This script helps set up the development environment for testing AI features

echo "🚀 AI-Driven Project Flow - Setup Script"
echo "==========================================="

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "✅ Created .env file from template"
    echo ""
    echo "📝 IMPORTANT: Please edit .env file and add your API keys:"
    echo "   - OPENAI_API_KEY=your-key-here"
    echo "   - ANTHROPIC_API_KEY=your-key-here" 
    echo "   - AI_PROVIDER=openai (or anthropic)"
    echo ""
else
    echo "✅ .env file exists"
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Check if database is running
echo "🔍 Checking database connection..."
python -c "
import os
from app.core.config import settings
from sqlalchemy import create_engine
try:
    engine = create_engine(settings.DATABASE_URL)
    connection = engine.connect()
    connection.close()
    print('✅ Database connection successful')
except Exception as e:
    print(f'⚠️  Database connection failed: {e}')
    print('💡 Make sure PostgreSQL is running on localhost:5433')
    print('   Or start it with: docker-compose up -d')
"

echo ""
echo "🎯 Setup Complete! Next steps:"
echo "1. Edit .env file with your AI API keys"
echo "2. Start the backend: uvicorn app.main:app --reload"
echo "3. Start the frontend: cd ../ai-driven-project-flow && npm run dev"
echo "4. Test AI validation at: http://localhost:8080/projects/create"
echo ""
echo "📚 API Documentation: http://localhost:8000/docs"
echo "🔧 AI Status Check: http://localhost:8000/api/v1/charter/status"
