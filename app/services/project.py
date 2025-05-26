from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from app.models.project import Project, ProjectStatus
from app.models.user import User
from app.schemas.project import ProjectCreateRequest, ProjectUpdateRequest, ProjectResponse
import json

class ProjectService:
    
    @staticmethod
    def create_project(db: Session, project_data: ProjectCreateRequest, owner_id: int) -> Project:
        """Create a new project"""
        
        # Parse charter if it's a string
        charter_data = project_data.charter
        if isinstance(project_data.charter, str):
            try:
                charter_data = json.loads(project_data.charter)
            except json.JSONDecodeError:
                # If not valid JSON, treat as description text
                charter_data = {"description": project_data.charter}
        
        # Extract project details from charter if available
        name = project_data.name
        description = project_data.description
        vision = project_data.vision
        problem_being_solved = project_data.problem_being_solved
        
        # If charter contains these fields, use them as fallback
        if charter_data:
            name = name or charter_data.get("name", "")
            description = description or charter_data.get("description", "")
            vision = vision or charter_data.get("vision", "")
            problem_being_solved = problem_being_solved or charter_data.get("problem_being_solved", "")
        
        db_project = Project(
            name=name,
            description=description,
            vision=vision,
            problem_being_solved=problem_being_solved,
            charter=charter_data,
            owner_id=owner_id,
            status=ProjectStatus.DRAFT,
            progress=0.0
        )
        
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project
    
    @staticmethod
    def get_project(db: Session, project_id: int, owner_id: int) -> Optional[Project]:
        """Get a project by ID (owned by user)"""
        return db.query(Project).filter(
            Project.id == project_id,
            Project.owner_id == owner_id
        ).first()
    
    @staticmethod
    def get_projects(
        db: Session, 
        owner_id: int, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None
    ) -> tuple[List[Project], int]:
        """Get projects for a user with optional search"""
        query = db.query(Project).filter(Project.owner_id == owner_id)
        
        # Add search filter if provided
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Project.name.ilike(search_term)) |
                (Project.description.ilike(search_term))
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        projects = query.order_by(desc(Project.updated_at)).offset(skip).limit(limit).all()
        
        return projects, total
    
    @staticmethod
    def update_project(
        db: Session, 
        project_id: int, 
        owner_id: int, 
        project_data: ProjectUpdateRequest
    ) -> Optional[Project]:
        """Update a project"""
        db_project = ProjectService.get_project(db, project_id, owner_id)
        if not db_project:
            return None
        
        # Update fields that are provided
        update_data = project_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_project, field, value)
        
        db.commit()
        db.refresh(db_project)
        return db_project
    
    @staticmethod
    def delete_project(db: Session, project_id: int, owner_id: int) -> bool:
        """Delete a project"""
        db_project = ProjectService.get_project(db, project_id, owner_id)
        if not db_project:
            return False
        
        db.delete(db_project)
        db.commit()
        return True
    
    @staticmethod
    def validate_charter(charter_text: str) -> dict:
        """Simulate AI validation of project charter"""
        # For now, return mock validation similar to frontend
        # This will be replaced with real AI validation later
        
        issues = []
        
        # Try to parse as JSON
        try:
            charter_data = json.loads(charter_text)
            
            # Check for common missing fields
            if not charter_data.get("name"):
                issues.append({
                    "field": "name",
                    "issue": "Project name is missing",
                    "suggestion": "Add a clear, descriptive project name"
                })
            
            if not charter_data.get("vision"):
                issues.append({
                    "field": "vision",
                    "issue": "Project vision is not defined",
                    "suggestion": "Add a vision statement describing the desired future state"
                })
            
            if not charter_data.get("risks"):
                issues.append({
                    "field": "risks",
                    "issue": "Risk assessment is missing",
                    "suggestion": "Identify potential risks and mitigation strategies"
                })
            
        except json.JSONDecodeError:
            # Not JSON, treat as text description
            if len(charter_text.strip()) < 50:
                issues.append({
                    "field": "description",
                    "issue": "Project description is too brief",
                    "suggestion": "Provide more detailed project description including scope, objectives, and expected outcomes"
                })
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "improved_charter": None  # Will be populated by AI later
        }
