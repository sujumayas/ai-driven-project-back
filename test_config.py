#!/usr/bin/env python3

"""
Quick test script to check if our configuration loads properly
"""

import os
import sys

# Add the app directory to Python path
sys.path.insert(0, '/app/app')

try:
    print("Testing configuration loading...")
    
    # Test environment variables
    print("\n1. Environment Variables:")
    env_vars = ['OPENAI_API_KEY', 'AI_PROVIDER', 'DATABASE_URL']
    for var in env_vars:
        value = os.getenv(var, 'NOT_SET')
        print(f"   {var}: {'SET' if value != 'NOT_SET' else 'NOT_SET'}")
    
    # Test settings import
    print("\n2. Settings Import:")
    from app.core.config import settings
    print(f"   ✅ Settings loaded successfully")
    print(f"   AI_PROVIDER: {settings.AI_PROVIDER}")
    print(f"   OPENAI_API_KEY: {'SET' if settings.OPENAI_API_KEY else 'NOT_SET'}")
    
    # Test AI provider
    print("\n3. AI Provider Test:")
    try:
        from app.services.ai import get_ai_provider
        provider = get_ai_provider()
        print(f"   ✅ AI Provider created: {provider.provider_name}")
    except Exception as e:
        print(f"   ⚠️  AI Provider failed: {e}")
    
    print("\n✅ Configuration test completed successfully!")

except Exception as e:
    print(f"\n❌ Configuration test failed: {e}")
    import traceback
    traceback.print_exc()
