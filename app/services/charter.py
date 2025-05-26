import json
from typing import Dict, Any, List, Optional
from app.services.ai import get_ai_provider_instance
from app.services.ai.base import ValidationIssue, CharterValidationResponse, SuggestionApplication

class CharterService:
    """Service for managing project charter operations with AI."""
    
    def __init__(self):
        self.ai_provider = None  # Initialize lazily
        
        # Expected charter format for validation
        self.expected_format = {
            "name": "string",
            "description": "string",
            "vision": "string",
            "problem_being_solved": "string",
            "scope": {
                "inside_scope": ["feature_1", "feature_2"],
                "outside_scope": ["feature_3"]
            },
            "modules": {
                "module_1": ["feature_1", "feature_2"],
                "module_2": ["feature_3"]
            },
            "risks": [
                {
                    "risk_name": "string",
                    "risk_impact": "string",
                    "risk_mitigation": "string"
                }
            ],
            "roadmap": [
                {
                    "starting_date": "2025-06-01",
                    "end_date": "2025-06-30",
                    "release_scope": ["module_1"]
                }
            ],
            "considerations": ["consideration_1"],
            "technical_considerations": ["tech_consideration_1"]
        }
    
    def _get_ai_provider(self):
        """Get AI provider instance, initialize if needed."""
        if self.ai_provider is None:
            try:
                self.ai_provider = get_ai_provider_instance()
            except Exception as e:
                # If AI provider fails to initialize, that's okay - we'll handle it later
                pass
        return self.ai_provider
    
    async def validate_charter(self, charter_text: str) -> CharterValidationResponse:
        """
        Validate a project charter using AI.
        
        Args:
            charter_text: The raw charter text (can be JSON or plain text)
            
        Returns:
            CharterValidationResponse with validation results
        """
        try:
            ai_provider = self._get_ai_provider()
            if ai_provider is None:
                raise Exception("AI provider not available")
                
            return await ai_provider.validate_charter(
                charter_text=charter_text,
                expected_format=self.expected_format
            )
        except Exception as e:
            raise Exception(f"Charter validation failed: {str(e)}")
    
    async def generate_suggestions(
        self, 
        charter: Dict[str, Any], 
        existing_issues: List[ValidationIssue]
    ) -> List[ValidationIssue]:
        """
        Generate additional improvement suggestions for a charter.
        
        Args:
            charter: The current charter data
            existing_issues: Already identified validation issues
            
        Returns:
            List of additional suggestions
        """
        try:
            ai_provider = self._get_ai_provider()
            if ai_provider is None:
                raise Exception("AI provider not available")
                
            return await ai_provider.generate_suggestions(
                charter=charter,
                issues=existing_issues
            )
        except Exception as e:
            raise Exception(f"Suggestion generation failed: {str(e)}")
    
    async def apply_suggestions(
        self, 
        charter: Dict[str, Any], 
        accepted_suggestions: List[ValidationIssue]
    ) -> SuggestionApplication:
        """
        Apply accepted suggestions to update the charter.
        
        Args:
            charter: The current charter data
            accepted_suggestions: List of accepted improvement suggestions
            
        Returns:
            SuggestionApplication with updated charter and application details
        """
        try:
            ai_provider = self._get_ai_provider()
            if ai_provider is None:
                raise Exception("AI provider not available")
                
            return await ai_provider.apply_suggestions(
                charter=charter,
                accepted_suggestions=accepted_suggestions
            )
        except Exception as e:
            raise Exception(f"Suggestion application failed: {str(e)}")
    
    def parse_charter_text(self, charter_text: str) -> Dict[str, Any]:
        """
        Parse charter text into structured format.
        
        Args:
            charter_text: Raw text input
            
        Returns:
            Parsed charter as dictionary
        """
        charter_text = charter_text.strip()
        
        # Try to parse as JSON first
        try:
            return json.loads(charter_text)
        except json.JSONDecodeError:
            # If not valid JSON, create a basic structure
            return {
                "name": "Project Charter",
                "description": charter_text[:500],  # First 500 chars as description
                "raw_input": charter_text  # Keep original for AI processing
            }
    
    def validate_charter_format(self, charter: Dict[str, Any]) -> List[str]:
        """
        Validate charter format against expected structure.
        
        Args:
            charter: Charter dictionary to validate
            
        Returns:
            List of format validation errors
        """
        errors = []
        
        # Check required fields
        required_fields = ["name", "description"]
        for field in required_fields:
            if field not in charter or not charter[field]:
                errors.append(f"Missing required field: {field}")
        
        # Check data types
        if "scope" in charter and not isinstance(charter["scope"], dict):
            errors.append("Scope must be an object with inside_scope and outside_scope arrays")
        
        if "modules" in charter and not isinstance(charter["modules"], dict):
            errors.append("Modules must be an object mapping module names to feature arrays")
        
        if "risks" in charter and not isinstance(charter["risks"], list):
            errors.append("Risks must be an array of risk objects")
        
        if "roadmap" in charter and not isinstance(charter["roadmap"], list):
            errors.append("Roadmap must be an array of release objects")
        
        return errors
    
    def get_charter_completeness_score(self, charter: Dict[str, Any]) -> float:
        """
        Calculate a completeness score for the charter.
        
        Args:
            charter: Charter to evaluate
            
        Returns:
            Completeness score between 0.0 and 1.0
        """
        total_sections = len(self.expected_format)
        completed_sections = 0
        
        for section in self.expected_format.keys():
            if section in charter and charter[section]:
                completed_sections += 1
        
        return completed_sections / total_sections if total_sections > 0 else 0.0
