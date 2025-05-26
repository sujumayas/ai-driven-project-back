from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class AIResponse(BaseModel):
    content: str
    usage: Optional[Dict[str, Any]] = None
    model: str
    provider: str

class ValidationIssue(BaseModel):
    field: str
    issue: str
    suggestion: str
    severity: str = "medium"  # low, medium, high

class CharterValidationResponse(BaseModel):
    is_valid: bool
    issues: List[ValidationIssue]
    structured_charter: Optional[Dict[str, Any]] = None
    completeness_score: float  # 0-1 scale

class SuggestionApplication(BaseModel):
    updated_charter: Dict[str, Any]
    applied_suggestions: List[str]
    conflicts: List[str] = []

class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    def __init__(self, api_key: str, model: str = None):
        self.api_key = api_key
        self.model = model
        self.provider_name = self.__class__.__name__.replace("Provider", "").lower()
    
    @abstractmethod
    async def generate_completion(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None
    ) -> AIResponse:
        """Generate text completion from prompt."""
        pass
    
    @abstractmethod
    async def validate_charter(
        self, 
        charter_text: str,
        expected_format: Optional[Dict[str, Any]] = None
    ) -> CharterValidationResponse:
        """Validate and analyze project charter."""
        pass
    
    @abstractmethod
    async def generate_suggestions(
        self, 
        charter: Dict[str, Any],
        issues: List[ValidationIssue]
    ) -> List[ValidationIssue]:
        """Generate improvement suggestions for charter."""
        pass
    
    @abstractmethod
    async def apply_suggestions(
        self, 
        charter: Dict[str, Any],
        accepted_suggestions: List[ValidationIssue]
    ) -> SuggestionApplication:
        """Apply accepted suggestions to charter."""
        pass
    
    def _format_system_prompt(self, base_prompt: str, **kwargs) -> str:
        """Format system prompt with variables."""
        return base_prompt.format(**kwargs)
