import openai
import json
import asyncio
from typing import Dict, Any, List, Optional
from .base import AIProvider, AIResponse, ValidationIssue, CharterValidationResponse, SuggestionApplication

class OpenAIProvider(AIProvider):
    """OpenAI GPT provider implementation."""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        super().__init__(api_key, model)
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.prompt_manager = None  # Initialize lazily to avoid circular imports
        
    def _get_prompt_manager(self):
        if self.prompt_manager is None:
            from app.services.prompt_manager import PromptManager
            self.prompt_manager = PromptManager()
        return self.prompt_manager
        
    async def generate_completion(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None
    ) -> AIResponse:
        """Generate text completion using OpenAI API."""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens or 2000
            )
            
            return AIResponse(
                content=response.choices[0].message.content,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                model=self.model,
                provider="openai"
            )
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    async def validate_charter(
        self, 
        charter_text: str,
        expected_format: Optional[Dict[str, Any]] = None
    ) -> CharterValidationResponse:
        """Validate project charter using OpenAI."""
        try:
            # Load validation prompt
            prompt_manager = self._get_prompt_manager()
            system_prompt = await prompt_manager.get_prompt(
                "charter_validation", 
                "system",
                version="v1.0"
            )
            
            user_prompt = await prompt_manager.get_prompt(
                "charter_validation",
                "user", 
                version="v1.0",
                charter_text=charter_text,
                expected_format=json.dumps(expected_format, indent=2) if expected_format else ""
            )
            
            response = await self.generate_completion(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.1
            )
            
            # Parse the JSON response
            result_data = json.loads(response.content)
            
            # Convert to our response format
            issues = [
                ValidationIssue(
                    field=issue["field"],
                    issue=issue["issue"],
                    suggestion=issue["suggestion"],
                    severity=issue.get("severity", "medium")
                )
                for issue in result_data.get("issues", [])
            ]
            
            return CharterValidationResponse(
                is_valid=result_data.get("is_valid", False),
                issues=issues,
                structured_charter=result_data.get("structured_charter"),
                completeness_score=result_data.get("completeness_score", 0.0)
            )
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse AI response as JSON: {str(e)}")
        except Exception as e:
            raise Exception(f"Charter validation failed: {str(e)}")
    
    async def generate_suggestions(
        self, 
        charter: Dict[str, Any],
        issues: List[ValidationIssue]
    ) -> List[ValidationIssue]:
        """Generate improvement suggestions using OpenAI."""
        try:
            prompt_manager = self._get_prompt_manager()
            system_prompt = await prompt_manager.get_prompt(
                "suggestion_generation",
                "system",
                version="v1.0"
            )
            
            user_prompt = await prompt_manager.get_prompt(
                "suggestion_generation",
                "user",
                version="v1.0",
                charter=json.dumps(charter, indent=2),
                existing_issues=json.dumps([issue.dict() for issue in issues], indent=2)
            )
            
            response = await self.generate_completion(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.2
            )
            
            result_data = json.loads(response.content)
            
            return [
                ValidationIssue(
                    field=suggestion["field"],
                    issue=suggestion["issue"],
                    suggestion=suggestion["suggestion"],
                    severity=suggestion.get("severity", "medium")
                )
                for suggestion in result_data.get("suggestions", [])
            ]
            
        except Exception as e:
            raise Exception(f"Suggestion generation failed: {str(e)}")
    
    async def apply_suggestions(
        self, 
        charter: Dict[str, Any],
        accepted_suggestions: List[ValidationIssue]
    ) -> SuggestionApplication:
        """Apply accepted suggestions to charter using OpenAI."""
        try:
            prompt_manager = self._get_prompt_manager()
            system_prompt = await prompt_manager.get_prompt(
                "suggestion_application",
                "system", 
                version="v1.0"
            )
            
            user_prompt = await prompt_manager.get_prompt(
                "suggestion_application",
                "user",
                version="v1.0",
                charter=json.dumps(charter, indent=2),
                suggestions=json.dumps([s.dict() for s in accepted_suggestions], indent=2)
            )
            
            response = await self.generate_completion(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.1
            )
            
            result_data = json.loads(response.content)
            
            return SuggestionApplication(
                updated_charter=result_data["updated_charter"],
                applied_suggestions=result_data.get("applied_suggestions", []),
                conflicts=result_data.get("conflicts", [])
            )
            
        except Exception as e:
            raise Exception(f"Suggestion application failed: {str(e)}")
