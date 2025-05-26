import os
import json
import yaml
from typing import Dict, Any, Optional
from pathlib import Path

class PromptManager:
    """Manages versioned AI prompts for different operations."""
    
    def __init__(self, prompts_dir: Optional[str] = None):
        if prompts_dir is None:
            # Get the prompts directory relative to this file
            current_file = Path(__file__)
            self.prompts_dir = current_file.parent.parent / "prompts"
        else:
            self.prompts_dir = Path(prompts_dir)
        
        self._prompt_cache: Dict[str, Dict[str, Any]] = {}
    
    async def get_prompt(
        self, 
        operation: str, 
        prompt_type: str, 
        version: str = "latest",
        **format_vars
    ) -> str:
        """
        Get a formatted prompt for a specific operation.
        
        Args:
            operation: The operation name (e.g., 'charter_validation')
            prompt_type: Type of prompt ('system', 'user', 'assistant')
            version: Version of the prompt to use
            **format_vars: Variables to format into the prompt template
        """
        cache_key = f"{operation}_{prompt_type}_{version}"
        
        if cache_key not in self._prompt_cache:
            prompt_data = await self._load_prompt(operation, version)
            self._prompt_cache[cache_key] = prompt_data
        
        prompt_content = self._prompt_cache[cache_key].get(prompt_type, "")
        
        if format_vars:
            try:
                return prompt_content.format(**format_vars)
            except KeyError as e:
                raise ValueError(f"Missing format variable {e} for prompt {cache_key}")
        
        return prompt_content
    
    async def _load_prompt(self, operation: str, version: str) -> Dict[str, Any]:
        """Load prompt from file system."""
        # Try YAML first, then JSON
        for ext in ['.yaml', '.yml', '.json']:
            file_path = self.prompts_dir / operation / f"{version}{ext}"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    if ext == '.json':
                        return json.load(f)
                    else:
                        return yaml.safe_load(f)
        
        # If version not found, try latest
        if version != "latest":
            return await self._load_prompt(operation, "latest")
        
        raise FileNotFoundError(f"Prompt file not found for operation '{operation}' version '{version}'")
    
    def list_operations(self) -> list:
        """List all available prompt operations."""
        if not self.prompts_dir.exists():
            return []
        
        return [d.name for d in self.prompts_dir.iterdir() if d.is_dir()]
    
    def list_versions(self, operation: str) -> list:
        """List all versions for a specific operation."""
        operation_dir = self.prompts_dir / operation
        if not operation_dir.exists():
            return []
        
        versions = []
        for file_path in operation_dir.iterdir():
            if file_path.is_file() and file_path.suffix in ['.yaml', '.yml', '.json']:
                versions.append(file_path.stem)
        
        return sorted(versions, reverse=True)  # Latest first
    
    def clear_cache(self):
        """Clear the prompt cache."""
        self._prompt_cache.clear()
