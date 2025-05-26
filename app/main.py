from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine
from app.models import Base
from app.api import projects, charter, test

app = FastAPI(
    title="AI-Driven Project Flow API",
    description="Backend API for SDLC management with AI-powered project planning",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup (for development)
# In production, use Alembic migrations instead
@app.on_event("startup")
async def startup_event():
    # Create tables on startup for development
    Base.metadata.create_all(bind=engine)
    print("Database tables created/verified")

@app.get("/")
async def root():
    return {"message": "AI-Driven Project Flow API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": settings.ENVIRONMENT}

# Include API routes
app.include_router(projects.router, prefix="/api/v1")
app.include_router(charter.router, prefix="/api/v1")
app.include_router(test.router, prefix="/api/v1")
