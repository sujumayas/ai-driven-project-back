from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from typing import List
import logging

from app.core.database import get_db
from app.services.release import ReleaseService
from app.services.project import ProjectService
from app.schemas.release import (
    ReleaseCreateRequest,
    ReleaseUpdateRequest,
    ReleaseResponse,
    ReleaseListResponse,
    ReleaseExtractionRequest,
    ReleaseExtractionResponse,
    ReleaseCreationFromExtractionRequest,
    BulkReleaseCreationResponse,
    ExtractedReleaseData,
)

router = APIRouter(prefix="/projects/{project_id}/releases", tags=["releases"])
logger = logging.getLogger(__name__)

# Temporary user ID for development (will be replaced with auth)
TEMP_USER_ID = 1


async def verify_project_access(project_id: int, db: Session) -> None:
    """Verify that the user has access to the project."""
    project = ProjectService.get_project(
        db=db, project_id=project_id, owner_id=TEMP_USER_ID
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")


@router.post("/extract", response_model=ReleaseExtractionResponse)
async def extract_release_plan(
    project_id: int = Path(..., description="Project ID"), db: Session = Depends(get_db)
):
    """
    Extract release plan from project charter using AI.

    This endpoint analyzes the project charter and uses AI to generate
    a structured release plan with recommendations.
    """
    try:
        await verify_project_access(project_id, db)

        # Get the project with charter
        project = ProjectService.get_project(
            db=db, project_id=project_id, owner_id=TEMP_USER_ID
        )
        if not project.charter:
            raise HTTPException(
                status_code=400,
                detail="Project charter is required for release extraction",
            )

        # Extract releases using AI
        release_service = ReleaseService()
        extraction_result = await release_service.extract_from_charter(project)

        return ReleaseExtractionResponse(
            extracted_releases=[
                ExtractedReleaseData(**release_data)
                for release_data in extraction_result.extracted_releases
            ],
            recommendations=extraction_result.recommendations,
            release_strategy=extraction_result.release_strategy,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Release extraction failed for project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Release extraction failed: {str(e)}"
        )


@router.post("/create-from-extraction", response_model=BulkReleaseCreationResponse)
async def create_releases_from_extraction(
    project_id: int = Path(..., description="Project ID"),
    request: ReleaseCreationFromExtractionRequest = ...,
    db: Session = Depends(get_db),
):
    """
    Create releases from AI extraction results.

    This endpoint takes the output from release extraction and creates
    the selected releases in the database.
    """
    try:
        await verify_project_access(project_id, db)

        created_releases = []
        failed_releases = []

        for release_index in request.selected_releases:
            try:
                if release_index >= len(request.extracted_data.extracted_releases):
                    failed_releases.append(
                        {"index": release_index, "error": "Release index out of range"}
                    )
                    continue

                release_data = request.extracted_data.extracted_releases[release_index]

                # Convert ExtractedReleaseData to dict for ReleaseService
                release_dict = {
                    "name": release_data.name,
                    "description": release_data.description,
                    "version": release_data.version,
                    "start_date": release_data.start_date,
                    "end_date": release_data.end_date,
                    "scope_modules": release_data.scope_modules,
                    "goals": release_data.goals,
                }

                db_release = ReleaseService.create_release(
                    db=db, project_id=project_id, release_data=release_dict
                )

                created_releases.append(ReleaseResponse.model_validate(db_release))

            except Exception as e:
                logger.error(f"Failed to create release {release_index}: {str(e)}")
                failed_releases.append({"index": release_index, "error": str(e)})

        return BulkReleaseCreationResponse(
            created_releases=created_releases,
            failed_releases=failed_releases,
            success_count=len(created_releases),
            total_count=len(request.selected_releases),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bulk release creation failed for project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Bulk release creation failed: {str(e)}"
        )


@router.get("/", response_model=ReleaseListResponse)
async def get_releases(
    project_id: int = Path(..., description="Project ID"), db: Session = Depends(get_db)
):
    """Get all releases for a project."""
    try:
        await verify_project_access(project_id, db)

        releases = ReleaseService.get_releases(db=db, project_id=project_id)

        return ReleaseListResponse(
            releases=[ReleaseResponse.model_validate(release) for release in releases],
            total=len(releases),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching releases for project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error fetching releases: {str(e)}"
        )


@router.post("/", response_model=ReleaseResponse)
async def create_release(
    project_id: int = Path(..., description="Project ID"),
    release_data: ReleaseCreateRequest = ...,
    db: Session = Depends(get_db),
):
    """Create a new release for the project."""
    try:
        await verify_project_access(project_id, db)

        # Convert Pydantic model to dict
        release_dict = release_data.model_dump()

        db_release = ReleaseService.create_release(
            db=db, project_id=project_id, release_data=release_dict
        )

        return ReleaseResponse.model_validate(db_release)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating release for project {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating release: {str(e)}")


@router.get("/{release_id}", response_model=ReleaseResponse)
async def get_release(
    project_id: int = Path(..., description="Project ID"),
    release_id: int = Path(..., description="Release ID"),
    db: Session = Depends(get_db),
):
    """Get a specific release."""
    try:
        await verify_project_access(project_id, db)

        db_release = ReleaseService.get_release(
            db=db, release_id=release_id, project_id=project_id
        )
        if not db_release:
            raise HTTPException(status_code=404, detail="Release not found")

        return ReleaseResponse.model_validate(db_release)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching release {release_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching release: {str(e)}")


@router.put("/{release_id}", response_model=ReleaseResponse)
async def update_release(
    project_id: int = Path(..., description="Project ID"),
    release_id: int = Path(..., description="Release ID"),
    release_data: ReleaseUpdateRequest = ...,
    db: Session = Depends(get_db),
):
    """Update a release."""
    try:
        await verify_project_access(project_id, db)

        # Convert Pydantic model to dict, excluding unset fields
        release_dict = release_data.model_dump(exclude_unset=True)

        db_release = ReleaseService.update_release(
            db=db,
            release_id=release_id,
            project_id=project_id,
            release_data=release_dict,
        )

        if not db_release:
            raise HTTPException(status_code=404, detail="Release not found")

        return ReleaseResponse.from_attributes(db_release)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating release {release_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating release: {str(e)}")


@router.delete("/{release_id}")
async def delete_release(
    project_id: int = Path(..., description="Project ID"),
    release_id: int = Path(..., description="Release ID"),
    db: Session = Depends(get_db),
):
    """Delete a release."""
    try:
        await verify_project_access(project_id, db)

        success = ReleaseService.delete_release(
            db=db, release_id=release_id, project_id=project_id
        )

        if not success:
            raise HTTPException(status_code=404, detail="Release not found")

        return {"message": "Release deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting release {release_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting release: {str(e)}")


@router.post("/{release_id}/update-progress")
async def update_release_progress(
    project_id: int = Path(..., description="Project ID"),
    release_id: int = Path(..., description="Release ID"),
    db: Session = Depends(get_db),
):
    """Update release progress based on epic completion."""
    try:
        await verify_project_access(project_id, db)

        # Verify release exists
        db_release = ReleaseService.get_release(
            db=db, release_id=release_id, project_id=project_id
        )
        if not db_release:
            raise HTTPException(status_code=404, detail="Release not found")

        ReleaseService.update_release_progress(db=db, release_id=release_id)

        # Return updated release
        updated_release = ReleaseService.get_release(
            db=db, release_id=release_id, project_id=project_id
        )
        return ReleaseResponse.from_attributes(updated_release)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating release progress {release_id}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error updating release progress: {str(e)}"
        )
