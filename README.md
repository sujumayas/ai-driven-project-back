# AI-Driven Project Flow - Backend API

This is the FastAPI backend for the AI-Driven Project Flow application.

## Features

- **FastAPI** framework with automatic OpenAPI documentation
- **PostgreSQL** database with SQLAlchemy ORM
- **Redis** for caching and background task queue
- **Celery** for asynchronous AI processing tasks
- **JWT Authentication** for secure API access
- **AI Integration** with OpenAI and Anthropic Claude APIs
- **Docker** support for easy deployment

## Quick Start

### Option 1: Docker (Recommended)

1. Copy environment file:
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

2. Start all services:
   ```bash
   docker-compose up -d
   ```

3. The API will be available at:
   - **API**: http://localhost:8000
   - **Documentation**: http://localhost:8000/docs
   - **Database**: localhost:5432
   - **Redis**: localhost:6379

### Option 2: Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up PostgreSQL and Redis locally

3. Copy and configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your database and API keys
   ```

4. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
app/
├── api/           # API route handlers
├── core/          # Core configuration and settings
├── models/        # Database models
├── services/      # Business logic and AI services
└── main.py        # FastAPI application entry point
```

## Environment Variables

See `.env.example` for all required environment variables.

Key variables:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`: AI service API keys
- `SECRET_KEY`: JWT signing key

## Development

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

### Testing

```bash
pytest
```

### Code Quality

```bash
# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```
