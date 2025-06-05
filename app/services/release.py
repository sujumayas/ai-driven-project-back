from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import json
import logging

from app.models.project import Project, Release, ReleaseStatus
from app.services.ai import get_ai_provider_instance
from app.services.prompt_manager import PromptManager
from app.services.ai.base import AIResponse

logger = logging.getLogger(__name__)


class ReleaseExtractionResponse:
    """Response model for release extraction results."""

    def __init__(
        self,
        extracted_releases: List[Dict[str, Any]],
        recommendations: List[Dict[str, Any]],
        release_strategy: Dict[str, Any],
    ):
        self.extracted_releases = extracted_releases
        self.recommendations = recommendations
        self.release_strategy = release_strategy


class ReleaseService:
    """Service for managing release operations with AI."""

    def __init__(self):
        self.prompt_manager = PromptManager()
        self.ai_provider = None

    def _get_ai_provider(self):
        """Get AI provider instance, initialize if needed."""
        if self.ai_provider is None:
            try:
                self.ai_provider = get_ai_provider_instance()
            except Exception as e:
                logger.warning(f"AI provider not available: {str(e)}")
        return self.ai_provider

    async def extract_from_charter(self, project: Project) -> ReleaseExtractionResponse:
        """
        Extract release plan from project charter using AI.

        Args:
            project: Project instance with charter data

        Returns:
            ReleaseExtractionResponse with extracted releases and recommendations
        """
        try:
            if not project.charter:
                raise ValueError("Project charter is required for release extraction")

            ai_provider = self._get_ai_provider()
            if ai_provider is None:
                raise Exception("AI provider not available")

            # Get the prompt template
            system_prompt = await self.prompt_manager.get_prompt(
                operation="release_extraction", prompt_type="system"
            )

            user_prompt = await self.prompt_manager.get_prompt(
                operation="release_extraction",
                prompt_type="user",
                charter_data=json.dumps(project.charter, indent=2),
            )

            # Generate AI response
            ai_response: AIResponse = await ai_provider.generate_completion(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.1,
                max_tokens=4000,
            )

            # Parse the AI response with robust JSON extraction
            try:
                # Log the raw response for debugging
                logger.info(f"Raw AI response length: {len(ai_response.content)}")
                logger.debug(f"Raw AI response: {ai_response.content[:500]}...")
                
                # Extract JSON from the response (handling markdown code blocks)
                json_content = ai_response.content.strip()
                
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
                
                logger.debug(f"Extracted JSON content: {json_content[:200]}...")
                
                # Parse the extracted JSON
                response_data = json.loads(json_content)
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response after extraction. Raw response: {ai_response.content}")
                logger.error(f"Attempted to parse: {json_content if 'json_content' in locals() else 'N/A'}")
                raise Exception(f"Invalid AI response format: {str(e)}")

            # Validate response structure
            if not all(
                key in response_data
                for key in ["extracted_releases", "recommendations", "release_strategy"]
            ):
                raise Exception("AI response missing required fields")

            return ReleaseExtractionResponse(
                extracted_releases=response_data["extracted_releases"],
                recommendations=response_data["recommendations"],
                release_strategy=response_data["release_strategy"],
            )

        except Exception as e:
            logger.error(f"Release extraction failed: {str(e)}")
            raise Exception(f"Release extraction failed: {str(e)}")

    @staticmethod
    def create_release(
        db: Session, project_id: int, release_data: Dict[str, Any]
    ) -> Release:
        """Create a new release for a project."""

        # Parse dates
        start_date = None
        end_date = None

        if release_data.get("start_date"):
            try:
                start_date = datetime.strptime(
                    release_data["start_date"], "%Y-%m-%d"
                ).date()
            except ValueError:
                logger.warning(
                    f"Invalid start_date format: {release_data['start_date']}"
                )

        if release_data.get("end_date"):
            try:
                end_date = datetime.strptime(
                    release_data["end_date"], "%Y-%m-%d"
                ).date()
            except ValueError:
                logger.warning(f"Invalid end_date format: {release_data['end_date']}")

        db_release = Release(
            name=release_data.get("name", "Release"),
            description=release_data.get("description"),
            version=release_data.get("version"),
            start_date=start_date,
            end_date=end_date,
            scope_modules=release_data.get("scope_modules", []),
            goals=release_data.get("goals", []),
            status=ReleaseStatus.NOT_STARTED,
            progress=0.0,
            project_id=project_id,
        )

        db.add(db_release)
        db.commit()
        db.refresh(db_release)
        return db_release

    @staticmethod
    def get_release(db: Session, release_id: int, project_id: int) -> Optional[Release]:
        """Get a release by ID within a project."""
        return (
            db.query(Release)
            .filter(Release.id == release_id, Release.project_id == project_id)
            .first()
        )

    @staticmethod
    def get_releases(db: Session, project_id: int) -> List[Release]:
        """Get all releases for a project."""
        return (
            db.query(Release)
            .filter(Release.project_id == project_id)
            .order_by(Release.start_date.asc(), Release.created_at.asc())
            .all()
        )

    @staticmethod
    def update_release(
        db: Session, release_id: int, project_id: int, release_data: Dict[str, Any]
    ) -> Optional[Release]:
        """Update a release."""
        db_release = ReleaseService.get_release(db, release_id, project_id)
        if not db_release:
            return None

        # Handle date parsing for updates
        if "start_date" in release_data and release_data["start_date"]:
            try:
                release_data["start_date"] = datetime.strptime(
                    release_data["start_date"], "%Y-%m-%d"
                ).date()
            except ValueError:
                del release_data["start_date"]  # Skip invalid dates

        if "end_date" in release_data and release_data["end_date"]:
            try:
                release_data["end_date"] = datetime.strptime(
                    release_data["end_date"], "%Y-%m-%d"
                ).date()
            except ValueError:
                del release_data["end_date"]  # Skip invalid dates

        # Update fields
        for field, value in release_data.items():
            if hasattr(db_release, field):
                setattr(db_release, field, value)

        db.commit()
        db.refresh(db_release)
        return db_release

    @staticmethod
    def delete_release(db: Session, release_id: int, project_id: int) -> bool:
        """Delete a release."""
        db_release = ReleaseService.get_release(db, release_id, project_id)
        if not db_release:
            return False

        db.delete(db_release)
        db.commit()
        return True

    @staticmethod
    def calculate_release_progress(db: Session, release_id: int) -> float:
        """Calculate progress for a release based on its epics."""
        release = db.query(Release).filter(Release.id == release_id).first()
        if not release or not release.epics:
            return 0.0

        total_epics = len(release.epics)
        completed_epics = sum(
            1 for epic in release.epics if epic.status.value == "Completed"
        )

        return (completed_epics / total_epics) * 100.0 if total_epics > 0 else 0.0

    @staticmethod
    def update_release_progress(db: Session, release_id: int):
        """Update release progress based on epic completion."""
        release = db.query(Release).filter(Release.id == release_id).first()
        if release:
            release.progress = ReleaseService.calculate_release_progress(db, release_id)
            db.commit()
