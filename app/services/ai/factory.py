from typing import Optional
from .base import AIProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from app.core.config import settings

def get_ai_provider(
    provider_name: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> AIProvider:
    """Factory function to get AI provider instance."""
    
    # Use provided values or fall back to settings
    provider = provider_name or settings.AI_PROVIDER
    
    if provider.lower() == "openai":
        key = api_key or settings.OPENAI_API_KEY
        if not key:
            raise ValueError("OpenAI API key not configured")
        return OpenAIProvider(api_key=key, model=model or "gpt-4")
    
    elif provider.lower() == "anthropic":
        key = api_key or settings.ANTHROPIC_API_KEY
        if not key:
            raise ValueError("Anthropic API key not configured")
        return AnthropicProvider(api_key=key, model=model or "claude-3-sonnet-20240229")
    
    else:
        raise ValueError(f"Unsupported AI provider: {provider}")

# Singleton instance for the application
_ai_provider_instance: Optional[AIProvider] = None

def get_ai_provider_instance() -> AIProvider:
    """Get singleton AI provider instance."""
    global _ai_provider_instance
    
    if _ai_provider_instance is None:
        _ai_provider_instance = get_ai_provider()
    
    return _ai_provider_instance

def reset_ai_provider_instance():
    """Reset singleton instance (useful for testing)."""
    global _ai_provider_instance
    _ai_provider_instance = None
