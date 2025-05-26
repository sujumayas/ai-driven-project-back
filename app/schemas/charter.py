from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class ValidationIssueSchema(BaseModel):
    field: str = Field(..., description="Field or section with the issue")
    issue: str = Field(..., description="Description of the problem")
    suggestion: str = Field(..., description="Specific recommendation")
    severity: str = Field(default="medium", description="Issue severity: low, medium, high")

class CharterValidationRequest(BaseModel):
    charter_text: str = Field(..., description="Raw charter text (JSON or plain text)")

class CharterValidationResponse(BaseModel):
    is_valid: bool = Field(..., description="Whether the charter is valid")
    completeness_score: float = Field(..., description="Completeness score (0.0-1.0)")
    issues: List[ValidationIssueSchema] = Field(default_factory=list, description="Validation issues found")
    structured_charter: Optional[Dict[str, Any]] = Field(None, description="Structured charter data if parseable")
    format_errors: List[str] = Field(default_factory=list, description="Format validation errors")

class SuggestionGenerationRequest(BaseModel):
    charter: Dict[str, Any] = Field(..., description="Current charter data")
    existing_issues: List[ValidationIssueSchema] = Field(default_factory=list, description="Existing validation issues")

class SuggestionGenerationResponse(BaseModel):
    suggestions: List[ValidationIssueSchema] = Field(..., description="Generated improvement suggestions")

class SuggestionApplicationRequest(BaseModel):
    charter: Dict[str, Any] = Field(..., description="Current charter data")
    accepted_suggestions: List[ValidationIssueSchema] = Field(..., description="Accepted suggestions to apply")

class SuggestionApplicationResponse(BaseModel):
    updated_charter: Dict[str, Any] = Field(..., description="Updated charter with suggestions applied")
    applied_suggestions: List[str] = Field(default_factory=list, description="Descriptions of applied changes")
    conflicts: List[str] = Field(default_factory=list, description="Any conflicts encountered during application")

class AIProviderStatus(BaseModel):
    provider: str = Field(..., description="Current AI provider (openai/anthropic)")
    model: str = Field(..., description="Current model being used")
    available: bool = Field(..., description="Whether the AI service is available")
    error: Optional[str] = Field(None, description="Error message if service is unavailable")

class CharterFormatExample(BaseModel):
    """Example response showing the expected charter format."""
    example: Dict[str, Any] = Field(..., description="Example charter structure")
    description: str = Field(..., description="Description of the format")
