#!/usr/bin/env python3
"""
Simple script to create a default user for development
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.user import User

def create_default_user():
    """Create a default user for development"""
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.id == 1).first()
        if existing_user:
            print(f"Default user already exists: {existing_user.email}")
            return True

        # Create default user
        default_user = User(
            email="demo@aiprojectflow.com",
            username="demo_user", 
            full_name="Demo User",
            is_active=True,
            is_verified=True
        )
        default_user.set_password("demo123!")
        
        db.add(default_user)
        db.commit()
        db.refresh(default_user)
        
        print(f"✅ Created default user: {default_user.email}")
        print(f"Password: demo123!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating default user: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    create_default_user()
