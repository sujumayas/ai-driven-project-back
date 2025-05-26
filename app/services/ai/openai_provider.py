import openai
import json
import asyncio
from typing import Dict, Any, List, Optional
from .base import AIProvider, AIResponse, ValidationIssue, CharterValidationResponse, SuggestionApplication

class OpenAIProvider(AIProvider):
    """OpenAI GPT provider implementation."""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo"):
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
            
            # Calculate safe token limits for comprehensive charter parsing
            # GPT-4-turbo has 128k context, allow for larger responses to capture complete charter
            # Estimate input tokens (rough approximation: 1 token ≈ 4 characters)
            estimated_input_tokens = len(user_prompt + (system_prompt or "")) // 4
            max_context = 120000 if "turbo" in self.model else 8000  # Use higher limit for turbo models
            safe_output_tokens = min(4000, max_context - estimated_input_tokens - 500)  # Increased for complete charter data
            
            if safe_output_tokens < 500:
                # Charter is too large, try to summarize it first
                print("Charter too large, attempting to summarize for validation")
                charter_summary = charter_text[:2000] + "\n[... content truncated for validation ...]" if len(charter_text) > 2000 else charter_text
                
                user_prompt = await prompt_manager.get_prompt(
                    "charter_validation",
                    "user", 
                    version="v1.0",
                    charter_text=charter_summary,
                    expected_format=json.dumps(expected_format, indent=2) if expected_format else ""
                )
                
                estimated_input_tokens = len(user_prompt + (system_prompt or "")) // 4
                safe_output_tokens = min(4000, max_context - estimated_input_tokens - 500)
                
                if safe_output_tokens < 500:
                    raise Exception("Charter too large for validation even after summarization. Please reduce the charter size.")
            
            print(f"Estimated input tokens: {estimated_input_tokens}, Output tokens: {safe_output_tokens}")
            
            response = await self.generate_completion(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.1,
                max_tokens=safe_output_tokens
            )
            
            # Debug: Log the raw response
            print(f"OpenAI Raw Response: '{response.content}'")
            print(f"Response length: {len(response.content)}")
            
            # Try to extract JSON from the response
            json_content = response.content.strip()
            
            # If response contains code blocks, extract the JSON
            if '```json' in json_content:
                start = json_content.find('```json') + 7
                end = json_content.find('```', start)
                if end > start:
                    json_content = json_content[start:end].strip()
            elif json_content.startswith('```') and json_content.endswith('```'):
                # Remove generic code block markers
                json_content = json_content[3:-3].strip()
            
            # Find the first { and last } to extract JSON object
            first_brace = json_content.find('{')
            last_brace = json_content.rfind('}')
            
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                json_content = json_content[first_brace:last_brace + 1]
            
            # Check if JSON appears to be truncated
            if not json_content.endswith('}'):
                print("WARNING: JSON response appears to be truncated")
                # Try to find a reasonable ending point
                # Look for the last complete object or array
                brackets = 0
                last_valid_pos = -1
                for i, char in enumerate(json_content):
                    if char == '{':
                        brackets += 1
                    elif char == '}':
                        brackets -= 1
                        if brackets == 0:
                            last_valid_pos = i + 1
                            break
                
                if last_valid_pos > 0:
                    json_content = json_content[:last_valid_pos]
                    print(f"Attempting to recover truncated JSON, cut at position {last_valid_pos}")
            
            print(f"Extracted JSON: '{json_content[:200]}...'")
            
            # Parse the JSON response
            result_data = json.loads(json_content)
            
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
            print(f"JSON Parse Error: {str(e)}")
            print(f"Raw content that failed to parse: '{response.content if 'response' in locals() else 'No response available'}'")
            print(f"Extracted content that failed to parse: '{json_content if 'json_content' in locals() else 'No extracted content'}'")
            raise Exception(f"Failed to parse AI response as JSON: {str(e)}")
        except Exception as e:
            print(f"General error in validate_charter: {str(e)}")
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
            
            # Calculate safe token limits for suggestion generation
            estimated_input_tokens = len(user_prompt + (system_prompt or "")) // 4
            max_context = 120000 if "turbo" in self.model else 8000
            safe_output_tokens = min(3000, max_context - estimated_input_tokens - 500)
            
            if safe_output_tokens < 500:
                raise Exception("Charter too large for suggestion generation.")
            
            print(f"Suggestion generation - Input tokens: {estimated_input_tokens}, Output tokens: {safe_output_tokens}")
            
            response = await self.generate_completion(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.2,
                max_tokens=safe_output_tokens
            )
            
            # Apply same JSON extraction logic as validation
            json_content = response.content.strip()
            
            if '```json' in json_content:
                start = json_content.find('```json') + 7
                end = json_content.find('```', start)
                if end > start:
                    json_content = json_content[start:end].strip()
            elif json_content.startswith('```') and json_content.endswith('```'):
                json_content = json_content[3:-3].strip()
            
            first_brace = json_content.find('{')
            last_brace = json_content.rfind('}')
            
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                json_content = json_content[first_brace:last_brace + 1]
            
            print(f"Suggestion JSON response: '{json_content[:200]}...'")
            
            result_data = json.loads(json_content)
            
            return [
                ValidationIssue(
                    field=suggestion["field"],
                    issue=suggestion["issue"],
                    suggestion=suggestion["suggestion"],
                    severity=suggestion.get("severity", "medium")
                )
                for suggestion in result_data.get("suggestions", [])
            ]
            
        except json.JSONDecodeError as e:
            print(f"Suggestion JSON Parse Error: {str(e)}")
            print(f"Raw suggestion content: '{response.content if 'response' in locals() else 'No response'}'")
            raise Exception(f"Failed to parse suggestion response as JSON: {str(e)}")
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
            
            # Calculate safe token limits for comprehensive charter updates
            estimated_input_tokens = len(user_prompt + (system_prompt or "")) // 4
            max_context = 120000 if "turbo" in self.model else 8000
            safe_output_tokens = min(5000, max_context - estimated_input_tokens - 500)  # Higher limit for complete charter updates
            
            if safe_output_tokens < 500:
                # Try with summarized charter
                charter_summary = {
                    "name": charter.get("name", ""),
                    "description": charter.get("description", ""),
                    "vision": charter.get("vision", ""),
                    "problem_being_solved": charter.get("problem_being_solved", "")
                }
                
                user_prompt = await prompt_manager.get_prompt(
                    "suggestion_application",
                    "user",
                    version="v1.0",
                    charter=json.dumps(charter_summary, indent=2),
                    suggestions=json.dumps([s.dict() for s in accepted_suggestions], indent=2)
                )
                
                estimated_input_tokens = len(user_prompt + (system_prompt or "")) // 4
                safe_output_tokens = min(5000, max_context - estimated_input_tokens - 500)
                
                if safe_output_tokens < 500:
                    raise Exception("Charter too large for suggestion application.")
            
            print(f"Apply suggestions - Input tokens: {estimated_input_tokens}, Output tokens: {safe_output_tokens}")
            
            response = await self.generate_completion(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.1,
                max_tokens=safe_output_tokens
            )
            
            # Apply same JSON extraction logic
            json_content = response.content.strip()
            
            print(f"Apply suggestions raw response: '{response.content[:300]}...'")
            
            if '```json' in json_content:
                start = json_content.find('```json') + 7
                end = json_content.find('```', start)
                if end > start:
                    json_content = json_content[start:end].strip()
            elif json_content.startswith('```') and json_content.endswith('```'):
                json_content = json_content[3:-3].strip()
            
            first_brace = json_content.find('{')
            last_brace = json_content.rfind('}')
            
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                json_content = json_content[first_brace:last_brace + 1]
            
            # Handle truncation for application responses
            if not json_content.endswith('}'):
                print("WARNING: Apply suggestions JSON appears truncated")
                brackets = 0
                last_valid_pos = -1
                for i, char in enumerate(json_content):
                    if char == '{':
                        brackets += 1
                    elif char == '}':
                        brackets -= 1
                        if brackets == 0:
                            last_valid_pos = i + 1
                            break
                
                if last_valid_pos > 0:
                    json_content = json_content[:last_valid_pos]
                    print(f"Recovered truncated apply suggestions JSON at position {last_valid_pos}")
            
            print(f"Apply suggestions extracted JSON: '{json_content[:200]}...'")
            
            result_data = json.loads(json_content)
            
            return SuggestionApplication(
                updated_charter=result_data.get("updated_charter", charter),  # Fallback to original
                applied_suggestions=result_data.get("applied_suggestions", []),
                conflicts=result_data.get("conflicts", [])
            )
            
        except json.JSONDecodeError as e:
            print(f"Apply suggestions JSON Parse Error: {str(e)}")
            print(f"Raw apply content: '{response.content if 'response' in locals() else 'No response'}'")
            print(f"Extracted apply content: '{json_content if 'json_content' in locals() else 'No extracted content'}'")
            raise Exception(f"Failed to parse suggestion application response as JSON: {str(e)}")
        except Exception as e:
            print(f"General error in apply_suggestions: {str(e)}")
            raise Exception(f"Suggestion application failed: {str(e)}")
