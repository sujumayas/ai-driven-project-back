from fastapi import APIRouter, HTTPException, Depends
from typing import List
import logging

from app.services.charter import CharterService
from app.services.ai import get_ai_provider_instance
from app.services.ai.base import ValidationIssue
from app.schemas.charter import (
    CharterValidationRequest,
    CharterValidationResponse,
    SuggestionGenerationRequest,
    SuggestionGenerationResponse,
    SuggestionApplicationRequest,
    SuggestionApplicationResponse,
    ValidationIssueSchema,
    AIProviderStatus,
    CharterFormatExample
)

router = APIRouter(prefix="/charter", tags=["charter"])
logger = logging.getLogger(__name__)

def get_charter_service() -> CharterService:
    """Dependency to get charter service instance."""
    return CharterService()

@router.post("/validate", response_model=CharterValidationResponse)
async def validate_charter(
    request: CharterValidationRequest,
    charter_service: CharterService = Depends(get_charter_service)
):
    """
    Validate a project charter using AI analysis.
    
    This endpoint:
    1. Analyzes the provided charter text
    2. Validates structure and completeness
    3. Identifies missing or incomplete sections
    4. Returns structured feedback with suggestions
    """
    try:
        logger.info(f"Validating charter with {len(request.charter_text)} characters")
        
        # First, try to parse and validate format
        parsed_charter = charter_service.parse_charter_text(request.charter_text)
        format_errors = charter_service.validate_charter_format(parsed_charter)
        
        # Run AI validation
        ai_validation = await charter_service.validate_charter(request.charter_text)
        
        # Calculate completeness score
        completeness_score = charter_service.get_charter_completeness_score(
            ai_validation.structured_charter or parsed_charter
        )
        
        # Convert AI response to schema format
        issues = [
            ValidationIssueSchema(
                field=issue.field,
                issue=issue.issue,
                suggestion=issue.suggestion,
                severity=issue.severity
            )
            for issue in ai_validation.issues
        ]
        
        return CharterValidationResponse(
            is_valid=ai_validation.is_valid and len(format_errors) == 0,
            completeness_score=max(ai_validation.completeness_score, completeness_score),
            issues=issues,
            structured_charter=ai_validation.structured_charter or parsed_charter,
            format_errors=format_errors
        )
        
    except Exception as e:
        logger.error(f"Charter validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Charter validation failed: {str(e)}")

@router.post("/suggestions", response_model=SuggestionGenerationResponse)
async def generate_suggestions(
    request: SuggestionGenerationRequest,
    charter_service: CharterService = Depends(get_charter_service)
):
    """
    Generate improvement suggestions for a project charter.
    
    This endpoint analyzes the charter and existing issues to provide
    additional actionable suggestions for improvement.
    """
    try:
        logger.info(f"Generating suggestions for charter: {request.charter.get('name', 'Unknown')}")
        
        # Convert schema to service format
        existing_issues = [
            ValidationIssue(
                field=issue.field,
                issue=issue.issue,
                suggestion=issue.suggestion,
                severity=issue.severity
            )
            for issue in request.existing_issues
        ]
        
        # Generate suggestions using AI
        ai_suggestions = await charter_service.generate_suggestions(
            charter=request.charter,
            existing_issues=existing_issues
        )
        
        # Convert back to schema format
        suggestions = [
            ValidationIssueSchema(
                field=suggestion.field,
                issue=suggestion.issue,
                suggestion=suggestion.suggestion,
                severity=suggestion.severity
            )
            for suggestion in ai_suggestions
        ]
        
        return SuggestionGenerationResponse(suggestions=suggestions)
        
    except Exception as e:
        logger.error(f"Suggestion generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Suggestion generation failed: {str(e)}")

@router.post("/apply-suggestions", response_model=SuggestionApplicationResponse)
async def apply_suggestions(
    request: SuggestionApplicationRequest,
    charter_service: CharterService = Depends(get_charter_service)
):
    """
    Apply accepted suggestions to update the project charter.
    
    This endpoint takes the current charter and a list of accepted suggestions,
    then uses AI to integrate the improvements into a cohesive updated charter.
    """
    try:
        logger.info(f"Applying {len(request.accepted_suggestions)} suggestions to charter")
        
        # Convert schema to service format
        accepted_suggestions = [
            ValidationIssue(
                field=suggestion.field,
                issue=suggestion.issue,
                suggestion=suggestion.suggestion,
                severity=suggestion.severity
            )
            for suggestion in request.accepted_suggestions
        ]
        
        # Apply suggestions using AI
        application_result = await charter_service.apply_suggestions(
            charter=request.charter,
            accepted_suggestions=accepted_suggestions
        )
        
        return SuggestionApplicationResponse(
            updated_charter=application_result.updated_charter,
            applied_suggestions=application_result.applied_suggestions,
            conflicts=application_result.conflicts
        )
        
    except Exception as e:
        logger.error(f"Suggestion application failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Suggestion application failed: {str(e)}")

@router.get("/status", response_model=AIProviderStatus)
async def get_ai_status():
    """
    Get the current AI provider status and availability.
    
    This endpoint checks if the AI service is properly configured and accessible.
    """
    try:
        ai_provider = get_ai_provider_instance()
        
        # Test the AI provider with a simple request
        test_response = await ai_provider.generate_completion(
            prompt="Test connection - respond with 'OK'",
            system_prompt="You are a test assistant. Respond with exactly 'OK'.",
            max_tokens=10
        )
        
        return AIProviderStatus(
            provider=ai_provider.provider_name,
            model=ai_provider.model,
            available=True,
            error=None
        )
        
    except Exception as e:
        logger.error(f"AI status check failed: {str(e)}")
        return AIProviderStatus(
            provider="unknown",
            model="unknown",
            available=False,
            error=str(e)
        )

@router.post("/debug-validate", response_model=dict)
async def debug_validate_charter(
    request: CharterValidationRequest
):
    """
    Debug endpoint for charter validation - returns what we receive.
    """
    return {
        "received_text": request.charter_text,
        "text_length": len(request.charter_text),
        "preview": request.charter_text[:200] + "..." if len(request.charter_text) > 200 else request.charter_text,
        "ai_provider_available": False,  # We'll check this
        "message": "Debug validation - no AI processing"
    }

@router.get("/format", response_model=CharterFormatExample)
async def get_charter_format():
    """
    Get the expected project charter format and structure.
    
    This endpoint returns an example of the expected charter structure
    to help users format their input correctly.
    """
    charter_service = CharterService()
    
    return CharterFormatExample(
        example=charter_service.expected_format,
        description="Expected project charter JSON structure with all supported fields and their formats."
    )
