#!/usr/bin/env python3
"""
Database reset script for AI-Driven Project Flow
This script drops all tables and recreates them, optionally with sample data containing proper charter structures
"""

import sys
import os
from datetime import date

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine, SessionLocal
from app.models import Base, User, Project, Release, Epic, UserStory, ProjectStatus, ReleaseStatus, EpicStatus, StoryStatus, StoryPriority
from app.core.config import settings

def drop_all_tables():
    """Drop all database tables"""
    print("Dropping all database tables...")
    try:
        Base.metadata.drop_all(bind=engine)
        print("✅ All tables dropped successfully!")
    except Exception as e:
        print(f"❌ Error dropping tables: {e}")
        return False
    return True

def create_tables():
    """Create database tables"""
    print("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        return False
    return True

def create_sample_charter_data():
    """Create sample projects with comprehensive charter data"""
    print("Creating sample projects with comprehensive charter data...")
    
    db = SessionLocal()
    try:
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

        # Create comprehensive charter data
        comprehensive_charter = {
            "business_context": {
                "vision": "Create the most intuitive e-commerce platform that adapts to user behavior and provides personalized shopping experiences",
                "problem_statement": "Current e-commerce platforms lack personalization, have poor conversion rates, and fail to understand customer preferences",
                "objectives": [
                    "Increase conversion rate by 25% within 6 months",
                    "Improve customer satisfaction score to 4.5/5",
                    "Reduce cart abandonment rate by 30%",
                    "Implement AI-driven product recommendations"
                ],
                "target_users": [
                    "Online shoppers aged 25-45",
                    "Mobile-first consumers",
                    "Price-conscious buyers",
                    "Technology enthusiasts"
                ],
                "market_analysis": "E-commerce market is growing at 15% annually with increasing demand for personalized experiences. Our target segment values convenience and personalization over price alone."
            },
            "technical_scope": {
                "modules": [
                    "User Authentication & Authorization",
                    "Product Catalog Management",
                    "Shopping Cart & Checkout",
                    "Payment Processing",
                    "AI Recommendation Engine",
                    "User Profile Management",
                    "Order Management",
                    "Analytics Dashboard"
                ],
                "technologies": [
                    "React 18 + TypeScript",
                    "Node.js + Express",
                    "PostgreSQL",
                    "Redis",
                    "Python ML Services",
                    "AWS Cloud Infrastructure",
                    "Docker & Kubernetes",
                    "Stripe Payment API"
                ],
                "architecture_overview": "Microservices architecture with React frontend, Node.js API gateway, Python ML services, and PostgreSQL database. Redis for caching and session management.",
                "integrations": [
                    "Stripe for payment processing",
                    "SendGrid for email notifications",
                    "AWS S3 for image storage",
                    "Google Analytics for tracking",
                    "Elasticsearch for search functionality"
                ],
                "technical_requirements": [
                    "99.9% uptime SLA",
                    "Sub-2-second page load times",
                    "Support for 10,000 concurrent users",
                    "GDPR and PCI DSS compliance",
                    "Mobile-responsive design"
                ]
            },
            "timeline": {
                "estimated_duration": "6 months",
                "phases": [
                    {
                        "name": "Phase 1: Core Platform",
                        "duration": "8 weeks",
                        "deliverables": [
                            "User authentication system",
                            "Product catalog with search",
                            "Basic shopping cart functionality",
                            "Payment integration"
                        ]
                    },
                    {
                        "name": "Phase 2: AI & Personalization",
                        "duration": "6 weeks",
                        "deliverables": [
                            "AI recommendation engine",
                            "User behavior tracking",
                            "Personalized product suggestions",
                            "Advanced search filters"
                        ]
                    },
                    {
                        "name": "Phase 3: Optimization & Launch",
                        "duration": "4 weeks",
                        "deliverables": [
                            "Performance optimization",
                            "Mobile app release",
                            "Analytics dashboard",
                            "Production deployment"
                        ]
                    }
                ],
                "milestones": [
                    {
                        "name": "MVP Launch",
                        "date": "2025-08-15",
                        "criteria": [
                            "Core shopping functionality working",
                            "Payment processing tested",
                            "Basic user accounts functional"
                        ]
                    },
                    {
                        "name": "AI Integration Complete",
                        "date": "2025-10-01",
                        "criteria": [
                            "Recommendation engine deployed",
                            "Personalization features active",
                            "User behavior analytics working"
                        ]
                    },
                    {
                        "name": "Production Launch",
                        "date": "2025-11-15",
                        "criteria": [
                            "All features tested and deployed",
                            "Performance benchmarks met",
                            "Marketing campaign launched"
                        ]
                    }
                ]
            },
            "resources": {
                "team_roles": [
                    "Product Manager",
                    "Frontend Developer (React)",
                    "Backend Developer (Node.js)",
                    "ML Engineer (Python)",
                    "DevOps Engineer",
                    "UI/UX Designer",
                    "QA Engineer",
                    "Data Analyst"
                ],
                "budget_estimate": "$750,000 - $1,000,000",
                "external_dependencies": [
                    "Stripe payment processing setup",
                    "AWS cloud infrastructure provisioning",
                    "Third-party API integrations",
                    "SSL certificates and domain setup"
                ],
                "required_skills": [
                    "React/TypeScript expertise",
                    "Node.js backend development",
                    "Machine Learning/AI",
                    "Cloud infrastructure (AWS)",
                    "Database design (PostgreSQL)",
                    "API design and integration"
                ]
            },
            "risks": [
                {
                    "risk": "AI recommendation model accuracy below expectations",
                    "impact": "High",
                    "mitigation": "Implement A/B testing framework and fallback to collaborative filtering. Allocate 2 weeks for model tuning and validation."
                },
                {
                    "risk": "Third-party payment processor downtime",
                    "impact": "High",
                    "mitigation": "Integrate multiple payment providers (Stripe + PayPal) and implement automatic failover mechanisms."
                },
                {
                    "risk": "Database performance issues under load",
                    "impact": "Medium",
                    "mitigation": "Implement database query optimization, add read replicas, and use Redis caching for frequently accessed data."
                },
                {
                    "risk": "Key team member departure",
                    "impact": "Medium",
                    "mitigation": "Maintain comprehensive documentation, implement pair programming, and cross-train team members on critical components."
                },
                {
                    "risk": "Scope creep from stakeholders",
                    "impact": "Low",
                    "mitigation": "Establish clear change management process and regular stakeholder review meetings to manage expectations."
                }
            ],
            "success_criteria": {
                "kpis": [
                    "Conversion rate increase of 25%",
                    "Average session duration > 5 minutes",
                    "Customer satisfaction score > 4.5/5",
                    "Cart abandonment rate < 20%",
                    "Monthly active users > 50,000"
                ],
                "acceptance_criteria": [
                    "All core e-commerce functionality operational",
                    "AI recommendations show 15% click-through rate",
                    "Page load times under 2 seconds",
                    "Mobile responsiveness on all major devices",
                    "99.9% uptime in production"
                ],
                "definition_of_done": [
                    "All features tested and code reviewed",
                    "Documentation complete and up-to-date",
                    "Performance benchmarks met",
                    "Security audit passed",
                    "Stakeholder acceptance confirmed"
                ]
            }
        }

        # Create the comprehensive project
        sample_project = Project(
            name="Commerce Revolution",
            description="Transform retail experience with AI-powered recommendations and personalized shopping",
            vision="Create the most intuitive e-commerce platform that adapts to user behavior",
            problem_being_solved="Current e-commerce platforms lack personalization and have poor conversion rates",
            status=ProjectStatus.IN_PLANNING,
            progress=25.0,
            charter=comprehensive_charter,
            owner_id=sample_user.id
        )
        db.add(sample_project)
        db.commit()
        db.refresh(sample_project)
        print(f"✅ Created comprehensive project: {sample_project.name}")

        # Create AI-format charter project (EGS Platform)
        ai_charter = {
            "name": "Renovación y Digitalización EGS",
            "description": "Renovación y completa digitalización de la plataforma EGS para promover desarrollo sostenible",
            "vision": "Convertir la plataforma EGS en producto digital innovador y escalable",
            "problem_being_solved": "Plataforma actual presenta limitaciones en experiencia de usuario y procesos no completamente digitalizados",
            "scope": {
                "inside_scope": [
                    "Investigación ágil sobre puntos de dolor",
                    "Diseño completo con 14 módulos",
                    "Implementación gradual en 3 fases",
                    "Digitalización completa del proceso",
                    "Desarrollo de sistemas de IA"
                ],
                "outside_scope": [
                    "Creación de contenido para capacitaciones",
                    "Desarrollo de aplicaciones móviles nativas",
                    "Integración con sistemas ERP externos"
                ]
            },
            "modules": {
                "Administrador": ["Gestión de ediciones", "Asignación de evaluaciones"],
                "Inscripción": ["Formulario de registro", "Firma digital"],
                "Evaluación": ["Sistema de calificación", "Generación de recomendaciones"]
            },
            "risks": [
                {
                    "risk_name": "Complejidad en implementación de IA",
                    "risk_impact": "Alto",
                    "risk_mitigation": "Análisis previo de fuentes y desarrollo de MVP"
                },
                {
                    "risk_name": "Resistencia al cambio",
                    "risk_impact": "Medio",
                    "risk_mitigation": "Plan de gestión del cambio con capacitaciones"
                }
            ],
            "roadmap": [
                {
                    "starting_date": "2024-01-01",
                    "end_date": "2024-04-30",
                    "release_scope": ["Módulo de usuarios", "Sistema de evaluación"]
                },
                {
                    "starting_date": "2024-05-01",
                    "end_date": "2024-08-31",
                    "release_scope": ["Módulo de reportes", "Sistema de IA"]
                }
            ],
            "technical_considerations": [
                "Frontend: React JS con diseño responsive",
                "Backend: Java 21 con Spring Suite",
                "Base de datos: PostgreSQL",
                "Infraestructura: AWS con EKS",
                "Seguridad: JWT con OAuth 2.0",
                "IA: Evaluación automática y continua"
            ]
        }

        ai_project = Project(
            name="Renovación EGS Platform",
            description="Digitalización completa de plataforma de sostenibilidad empresarial",
            vision="Plataforma digital innovadora para evaluación de sostenibilidad",
            problem_being_solved="Limitaciones en experiencia de usuario y procesos manuales",
            status=ProjectStatus.DRAFT,
            progress=15.0,
            charter=ai_charter,
            owner_id=sample_user.id
        )
        db.add(ai_project)
        db.commit()
        db.refresh(ai_project)
        print(f"✅ Created AI-format project: {ai_project.name}")

        # Create a second project with simpler charter
        simple_charter = {
            "business_context": {
                "vision": "Develop a modern task management application for remote teams",
                "problem_statement": "Remote teams struggle with task coordination and project visibility",
                "objectives": [
                    "Improve team productivity by 20%",
                    "Reduce project delivery time by 15%",
                    "Increase team collaboration satisfaction"
                ],
                "target_users": ["Remote teams", "Project managers", "Small businesses"]
            },
            "technical_scope": {
                "modules": ["Task Management", "Team Collaboration", "Project Dashboard", "Notifications"],
                "technologies": ["React", "Node.js", "MongoDB", "Socket.io"],
                "architecture_overview": "Single-page application with real-time updates and cloud deployment"
            },
            "risks": [
                {
                    "risk": "Competition from established tools like Asana",
                    "impact": "Medium",
                    "mitigation": "Focus on unique features for remote teams and competitive pricing"
                }
            ]
        }

        simple_project = Project(
            name="TaskFlow Pro",
            description="Modern task management for remote teams",
            vision="Streamline remote team collaboration",
            problem_being_solved="Remote teams lack effective task coordination tools",
            status=ProjectStatus.DRAFT,
            progress=5.0,
            charter=simple_charter,
            owner_id=sample_user.id
        )
        db.add(simple_project)
        db.commit()
        db.refresh(simple_project)
        print(f"✅ Created simple project: {simple_project.name}")

        print("🎉 Sample charter data created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating sample charter data: {e}")
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

def main():
    """Main reset function"""
    print("🔄 AI-Driven Project Flow Database Reset")
    print("=" * 50)
    print("⚠️  WARNING: This will delete ALL existing data!")
    
    # Confirm reset
    while True:
        confirm = input("\n❓ Are you sure you want to reset the database? (y/n): ").lower().strip()
        if confirm in ['y', 'yes']:
            break
        elif confirm in ['n', 'no']:
            print("❌ Database reset cancelled")
            return 0
        else:
            print("Please enter 'y' or 'n'")
    
    # Check database connection
    if not check_database_connection():
        print("❌ Database reset failed!")
        return 1
    
    # Drop and recreate tables
    if not drop_all_tables():
        print("❌ Database reset failed!")
        return 1
        
    if not create_tables():
        print("❌ Database reset failed!")
        return 1
    
    # Ask user if they want to create sample charter data
    while True:
        seed_choice = input("\n🌱 Create sample projects with comprehensive charter data? (y/n): ").lower().strip()
        if seed_choice in ['y', 'yes']:
            if not create_sample_charter_data():
                print("❌ Sample data creation failed!")
                return 1
            break
        elif seed_choice in ['n', 'no']:
            print("ℹ️  Database reset complete - no sample data created")
            break
        else:
            print("Please enter 'y' or 'n'")
    
    print("\n🎉 Database reset completed successfully!")
    print("\nNext steps:")
    print("1. Start the FastAPI server: uvicorn app.main:app --reload")
    print("2. Access API docs at: http://localhost:8000/docs") 
    print("3. Test the frontend charter display with new data")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
