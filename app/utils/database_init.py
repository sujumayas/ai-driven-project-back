#!/usr/bin/env python3
"""
Database initialization utility for AI-Driven Project Flow
This script creates the database tables and can seed initial data
"""

import sys
from datetime import date
from sqlalchemy import text
from ..core.database import engine, SessionLocal
from ..models import Base, User, Project, Release, Epic, UserStory, ProjectStatus, ReleaseStatus, EpicStatus, StoryStatus, StoryPriority
from ..core.config import settings

def create_database():
    """Create database tables"""
    print("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        return False
    return True

def seed_sample_data():
    """Seed the database with sample data for development"""
    print("Seeding sample data...")
    
    db = SessionLocal()
    try:
        # Check if data already exists
        existing_user = db.query(User).filter(User.email == "demo@aiprojectflow.com").first()
        if existing_user:
            print("ℹ️  Sample data already exists, skipping...")
            return True

        # Create a sample user
        sample_user = User(
            email="demo@aiprojectflow.com",
            username="demo_user",
            full_name="Demo User",
            is_active=True,
            is_verified=True
        )
        sample_user.set_password("demo123!")
        db.add(sample_user)
        db.commit()
        db.refresh(sample_user)
        print(f"✅ Created sample user: {sample_user.email}")

        # Create a sample project
        sample_project = Project(
            name="Commerce Revolution",
            description="Transform retail experience with AI-powered recommendations",
            vision="Create the most intuitive e-commerce platform that adapts to user behavior",
            problem_being_solved="Current e-commerce platforms lack personalization and have poor conversion rates",
            status=ProjectStatus.IN_PLANNING,
            progress=15.0,
            charter={
                "business_goals": ["Increase conversion rate by 25%", "Improve user engagement"],
                "success_metrics": ["Conversion rate", "User retention", "Revenue per user"],
                "constraints": ["6-month timeline", "Budget: $500K", "Team of 8 developers"]
            },
            owner_id=sample_user.id
        )
        db.add(sample_project)
        db.commit()
        db.refresh(sample_project)
        print(f"✅ Created sample project: {sample_project.name}")

        # Create sample releases
        release_1 = Release(
            name="R-1",
            description="Core e-commerce functionality with basic AI recommendations",
            version="1.0.0",
            start_date=date(2025, 6, 1),
            end_date=date(2025, 6, 30),
            scope_modules=["Auth", "Catalog", "Payments", "Basic Recommendations"],
            progress=25.0,
            status=ReleaseStatus.PLANNING,
            goals=["Implement core shopping flow", "Basic AI recommendation engine"],
            project_id=sample_project.id
        )
        
        release_2 = Release(
            name="R-2", 
            description="Advanced personalization and loyalty features",
            version="2.0.0",
            start_date=date(2025, 7, 5),
            end_date=date(2025, 8, 15),
            scope_modules=["Loyalty", "CMS", "Advanced AI", "Analytics"],
            progress=0.0,
            status=ReleaseStatus.NOT_STARTED,
            goals=["Implement loyalty program", "Advanced personalization"],
            project_id=sample_project.id
        )
        
        db.add_all([release_1, release_2])
        db.commit()
        db.refresh(release_1)
        db.refresh(release_2)
        print(f"✅ Created sample releases: {release_1.name}, {release_2.name}")

        # Create sample epics
        epic_1 = Epic(
            name="Catalog Browsing",
            description="Search & facets MVP with AI-powered recommendations",
            version="v1",
            status=EpicStatus.DRAFT,
            progress=0.0,
            acceptance_criteria=[
                "Users can search for products by name, category, brand",
                "Search results include AI-powered recommendations",
                "Filtering by price, rating, availability works correctly"
            ],
            business_value="Enables customers to find products quickly and discover relevant items",
            technical_notes="Implement Elasticsearch for search, ML pipeline for recommendations",
            architecture_notes="Microservices architecture with search service and recommendation engine",
            release_id=release_1.id
        )
        
        epic_2 = Epic(
            name="Checkout Flow",
            description="3-step checkout process with payment integration",
            version="v2", 
            status=EpicStatus.READY,
            progress=0.0,
            acceptance_criteria=[
                "Guest and registered user checkout flows",
                "Multiple payment methods (card, PayPal, digital wallets)",
                "Order confirmation and tracking"
            ],
            business_value="Streamlined checkout reduces cart abandonment",
            technical_notes="Integration with Stripe, PayPal APIs",
            architecture_notes="Secure payment processing with PCI compliance",
            release_id=release_1.id
        )
        
        db.add_all([epic_1, epic_2])
        db.commit()
        db.refresh(epic_1)
        db.refresh(epic_2)
        print(f"✅ Created sample epics: {epic_1.name}, {epic_2.name}")

        # Create sample user stories
        story_1 = UserStory(
            name="US-001: Product Search",
            description="As a customer, I want to search for products so that I can find what I need quickly",
            story_points=5,
            status=StoryStatus.DRAFT,
            priority=StoryPriority.HIGH,
            acceptance_criteria=[
                "Search bar is visible on all product pages",
                "Search returns relevant results within 2 seconds",
                "Search suggestions appear as user types",
                "No results found message displayed when appropriate"
            ],
            business_value="Core functionality for product discovery",
            technical_notes="Use Elasticsearch for full-text search, implement auto-suggestions",
            architecture_recommendations=[
                "Use dedicated search microservice",
                "Implement caching for common searches",
                "Add search analytics tracking"
            ],
            epic_id=epic_1.id,
            assignee_id=sample_user.id
        )
        
        story_2 = UserStory(
            name="US-002: Filter Products",
            description="As a customer, I want to filter products by category, price, and rating so I can narrow down my search",
            story_points=3,
            status=StoryStatus.READY,
            priority=StoryPriority.MEDIUM,
            acceptance_criteria=[
                "Filter sidebar with categories, price ranges, ratings",
                "Multiple filters can be applied simultaneously",
                "Filter results update without page refresh",
                "Clear all filters option available"
            ],
            business_value="Improves user experience by helping customers find relevant products",
            technical_notes="Use faceted search with Elasticsearch aggregations",
            architecture_recommendations=[
                "Client-side state management for filters",
                "API endpoint for filter aggregations",
                "URL-based filter state for sharing"
            ],
            epic_id=epic_1.id,
            assignee_id=sample_user.id
        )
        
        db.add_all([story_1, story_2])
        db.commit()
        print(f"✅ Created sample user stories: {story_1.name}, {story_2.name}")

        print("🎉 Sample data seeding completed successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding sample data: {e}")
        db.rollback()
        return False
    finally:
        db.close()
    
    return True

def check_database_connection():
    """Test database connection"""
    print("Testing database connection...")
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Database connection successful!")
            print(f"PostgreSQL version: {version}")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Make sure PostgreSQL is running and database credentials are correct")
        return False
    return True

def initialize_database(seed_data: bool = False):
    """Initialize database with optional sample data"""
    print("🚀 AI-Driven Project Flow Database Initialization")
    print("=" * 50)
    
    # Check database connection
    if not check_database_connection():
        print("❌ Database initialization failed!")
        return False
    
    # Create tables
    if not create_database():
        print("❌ Database initialization failed!")
        return False
    
    # Seed sample data if requested
    if seed_data:
        if not seed_sample_data():
            print("❌ Sample data seeding failed!")
            return False
    
    print("\n🎉 Database initialization completed successfully!")
    return True
