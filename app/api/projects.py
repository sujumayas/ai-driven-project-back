from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import math

from app.core.database import get_db
from app.services.project import ProjectService
from app.schemas.project import (
    ProjectCreateRequest, 
    ProjectUpdateRequest, 
    ProjectResponse, 
    ProjectListResponse,
    CharterValidationResponse
)

router = APIRouter(prefix="/projects", tags=["projects"])

# Temporary user ID for development (will be replaced with auth)
TEMP_USER_ID = 1

@router.post("/", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a new project"""
    try:
        db_project = ProjectService.create_project(
            db=db, 
            project_data=project_data, 
            owner_id=TEMP_USER_ID
        )
        return ProjectResponse.from_orm_with_frontend_compat(db_project)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating project: {str(e)}")

@router.get("/", response_model=ProjectListResponse)
async def get_projects(
    skip: int = Query(0, ge=0, description="Number of projects to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of projects to return"),
    search: Optional[str] = Query(None, description="Search term for project name or description"),
    db: Session = Depends(get_db)
):
    """Get projects for the current user"""
    try:
        projects, total = ProjectService.get_projects(
            db=db,
            owner_id=TEMP_USER_ID,
            skip=skip,
            limit=limit,
            search=search
        )
        
        # Convert to response format
        project_responses = [
            ProjectResponse.from_orm_with_frontend_compat(project) 
            for project in projects
        ]
        
        total_pages = math.ceil(total / limit) if total > 0 else 0
        current_page = (skip // limit) + 1
        
        return ProjectListResponse(
            projects=project_responses,
            total=total,
            page=current_page,
            size=len(project_responses),
            total_pages=total_pages
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching projects: {str(e)}")

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific project"""
    db_project = ProjectService.get_project(db=db, project_id=project_id, owner_id=TEMP_USER_ID)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return ProjectResponse.from_orm_with_frontend_compat(db_project)

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update a project"""
    db_project = ProjectService.update_project(
        db=db,
        project_id=project_id,
        owner_id=TEMP_USER_ID,
        project_data=project_data
    )
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return ProjectResponse.from_orm_with_frontend_compat(db_project)

@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """Delete a project"""
    success = ProjectService.delete_project(
        db=db, 
        project_id=project_id, 
        owner_id=TEMP_USER_ID
    )
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {"message": "Project deleted successfully"}

@router.post("/validate-charter", response_model=CharterValidationResponse)
async def validate_charter(
    charter_text: str
):
    """Validate project charter using AI (simulated for now)"""
    try:
        validation_result = ProjectService.validate_charter(charter_text)
        return CharterValidationResponse(**validation_result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error validating charter: {str(e)}")
