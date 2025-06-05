# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI backend for an AI-driven SDLC (Software Development Life Cycle) management system. The application manages software projects with AI-powered features for charter validation, project planning, and requirements management using OpenAI and Anthropic APIs.

## Architecture

### Core Structure
- **FastAPI** with async/await patterns throughout
- **SQLAlchemy 2.0** ORM with PostgreSQL database
- **Alembic** for database migrations
- **Celery + Redis** for background task processing
- **AI Provider abstraction** supporting OpenAI and Anthropic

### Key Components
- `/app/api/` - FastAPI routers (projects, charter, test)
- `/app/models/` - SQLAlchemy models with hierarchical project structure
- `/app/services/` - Business logic layer with AI integration
- `/app/core/` - Configuration, database, and logging setup
- `/app/schemas/` - Pydantic models for request/response validation
- `/app/prompts/` - Versioned YAML prompt templates for AI operations

### Database Hierarchy
```
User → Project → Release → Epic → UserStory → UseCase/TestCase
```

## Development Commands

### Environment Setup
```bash
# Complete environment setup
./setup.sh

# Docker environment
./rebuild-docker.sh
```

### Database Management
```bash
# Initialize database with tables
python manage.py init-db

# Initialize with sample data
python manage.py init-db-seed

# Direct scripts
python scripts/init_db.py        # Interactive setup with sample data
python scripts/reset_db.py       # Reset database
python scripts/clear_projects.py # Clear project data only
```

### Docker Operations
```bash
# Start services
docker-compose up -d

# Rebuild and restart
./rebuild-docker.sh

# Quick rebuild (development)
./quick-rebuild.sh
```

### Database Migrations
```bash
# Generate migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## Configuration

### Environment Variables
Key settings in `.env`:
- `DATABASE_URL` - PostgreSQL connection
- `REDIS_URL` - Redis connection  
- `OPENAI_API_KEY` - OpenAI integration
- `ANTHROPIC_API_KEY` - Anthropic integration

### AI Provider System
- Factory pattern in `services/ai/factory.py`
- Switch providers via `AI_PROVIDER` environment variable
- Prompts are versioned YAML files in `/app/prompts/`

## Testing & Quality

### Running Tests
```bash
pytest                    # All tests
pytest app/tests/        # Specific directory
pytest -v                # Verbose output
```

### Code Quality
```bash
black .                   # Code formatting
flake8 .                  # Linting
mypy .                    # Type checking
```

## API Structure

### Base URL
`/api/v1` - All endpoints use this prefix

### Key Endpoints
- `/projects` - Project CRUD with search/pagination
- `/charter/validate` - AI-powered charter validation
- `/charter/suggestions` - Generate improvement suggestions
- `/charter/apply-suggestions` - Apply AI recommendations

### Authentication
Currently uses `TEMP_USER_ID = 1` for development. JWT infrastructure is configured but not actively used.

## AI Integration

### Charter Validation Flow
1. Parse charter (JSON or text)
2. Validate format and completeness
3. Generate AI suggestions via prompt templates
4. Return structured feedback with scores

### Prompt Management
- Templates in `/app/prompts/{operation}/latest.yaml`
- Version control with fallback to `v1.0.yaml`
- Variables: `{charter_text}`, `{suggestions}`, etc.

## Development Notes

### Docker Services
- **API**: FastAPI application (port 8000)
- **PostgreSQL**: Database (port 5433)
- **Redis**: Cache/queue (port 6380)
- **Celery**: Background worker

### Database Models
- Use hybrid properties for computed values (progress, counts)
- JSON fields for flexible data (charter, acceptance criteria)
- Enum-based status tracking across all models
- Automatic audit trails with created_at/updated_at

### Frontend Integration
- CORS configured for ports 8080, 5173, 3000
- Response schemas designed for TypeScript compatibility
- Error handling with meaningful HTTP status codes