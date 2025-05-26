#!/usr/bin/env python3
"""
Management commands for AI-Driven Project Flow
"""

import sys
import asyncio
from app.utils.database_init import initialize_database

def main():
    if len(sys.argv) < 2:
        print("Usage: python manage.py <command>")
        print("Commands:")
        print("  init-db        Initialize database tables")
        print("  init-db-seed   Initialize database with sample data")
        return 1
    
    command = sys.argv[1]
    
    if command == "init-db":
        success = initialize_database(seed_data=False)
        return 0 if success else 1
    elif command == "init-db-seed":
        success = initialize_database(seed_data=True)
        return 0 if success else 1
    else:
        print(f"Unknown command: {command}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
