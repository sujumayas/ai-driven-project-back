#!/usr/bin/env python3
"""
Clear projects script - removes only project data while keeping users
"""

import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import SessionLocal
from app.models import Project, Release, Epic, UserStory, UseCase, TestCase, Comment

def clear_projects():
    """Clear all project-related data"""
    print("Clearing all project data...")
    
    db = SessionLocal()
    try:
        # Delete in correct order to avoid foreign key constraints
        db.query(Comment).delete()
        db.query(TestCase).delete() 
        db.query(UseCase).delete()
        db.query(UserStory).delete()
        db.query(Epic).delete()
        db.query(Release).delete()
        db.query(Project).delete()
        
        db.commit()
        print("✅ All project data cleared successfully!")
        
    except Exception as e:
        print(f"❌ Error clearing project data: {e}")
        db.rollback()
        return False
    finally:
        db.close()
    
    return True

def main():
    """Main function"""
    print("🗑️  Clear Project Data")
    print("=" * 30)
    print("This will remove all projects, releases, epics, and stories")
    print("User accounts will be preserved")
    
    # Confirm action
    while True:
        confirm = input("\n❓ Continue? (y/n): ").lower().strip()
        if confirm in ['y', 'yes']:
            break
        elif confirm in ['n', 'no']:
            print("❌ Operation cancelled")
            return 0
        else:
            print("Please enter 'y' or 'n'")
    
    if clear_projects():
        print("\n🎉 Project data cleared successfully!")
        print("You can now create new projects with proper charter structures")
    else:
        print("❌ Failed to clear project data")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
