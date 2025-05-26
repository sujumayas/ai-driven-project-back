from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "AI-Driven Project Flow API"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    
    # Database settings
    DATABASE_URL: str = "postgresql://username:password@localhost:5433/ai_project_flow"
    
    # Redis settings (for caching and task queue)
    REDIS_URL: str = "redis://localhost:6380"
    
    # AI Service settings
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    AI_PROVIDER: str = "openai"  # or "anthropic"
    AI_MODEL: Optional[str] = None  # Use provider defaults if not specified
    AI_TEMPERATURE: float = 0.1
    AI_MAX_TOKENS: int = 2000
    
    # Prompt settings
    PROMPTS_DIR: Optional[str] = None  # Use default if not specified
    PROMPT_VERSION: str = "v1.0"
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
