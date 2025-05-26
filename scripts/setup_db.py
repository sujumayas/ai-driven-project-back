#!/usr/bin/env python3
"""
Quick setup script to initialize the database and create a test user
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, SessionLocal
from app.models import Base, User, Project, ProjectStatus
from sqlalchemy import text

def setup_database():
    """Complete database setup"""
    print("🚀 Setting up AI-Driven Project Flow Database...")
    
    # Test database connection
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Database connection successful!")
            print(f"PostgreSQL version: {version}")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Please make sure PostgreSQL is running:")
        print("- Via Docker: cd to backend folder and run 'docker-compose up db'")
        print("- Or install PostgreSQL locally with the credentials in .env")
        return False
    
    # Create tables
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    
    # Create default user
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.id == 1).first()
        if existing_user:
            print(f"✅ Default user already exists: {existing_user.email}")
        else:
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
            print(f"   Password: demo123!")
        
        # Create a sample project if none exists
        existing_project = db.query(Project).first()
        if not existing_project:
            sample_project = Project(
                name="Sample Project",
                description="A sample project to test the integration",
                vision="Demonstrate full-stack connectivity",
                problem_being_solved="Testing the connection between frontend and backend",
                status=ProjectStatus.DRAFT,
                progress=10.0,
                charter={
                    "name": "Sample Project",
                    "description": "A sample project to test the integration",
                    "business_goals": ["Test frontend-backend connection", "Validate data persistence"]
                },
                owner_id=1
            )
            db.add(sample_project)
            db.commit()
            print("✅ Created sample project for testing")
        
    except Exception as e:
        print(f"❌ Error setting up data: {e}")
        db.rollback()
        return False
    finally:
        db.close()
    
    print("\n🎉 Database setup complete!")
    print("\nYou can now:")
    print("1. Start the backend: uvicorn app.main:app --reload")
    print("2. Start the frontend: npm run dev")
    print("3. Visit http://localhost:8080/projects")
    
    return True

if __name__ == "__main__":
    setup_database()
