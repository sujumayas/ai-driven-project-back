from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ProjectStatus(str, Enum):
    DRAFT = "Draft"
    IN_PLANNING = "In Planning"
    IN_DEVELOPMENT = "In Development"
    IN_REVIEW = "In Review"
    COMPLETED = "Completed"
    ON_HOLD = "On Hold"
    CANCELLED = "Cancelled"

# Request schemas
class ProjectCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    vision: Optional[str] = Field(None, description="Project vision statement")
    problem_being_solved: Optional[str] = Field(None, description="Problem being solved")
    charter: Optional[Dict[str, Any]] = Field(None, description="Project charter JSON")
    
class ProjectUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    vision: Optional[str] = None
    problem_being_solved: Optional[str] = None
    status: Optional[ProjectStatus] = None
    progress: Optional[float] = Field(None, ge=0, le=100)
    charter: Optional[Dict[str, Any]] = None

# Response schemas
class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    vision: Optional[str]
    problem_being_solved: Optional[str]
    status: ProjectStatus
    progress: float
    charter: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    owner_id: int
    
    # Frontend compatibility - matching the expected interface
    lastUpdate: str  # Will be computed from updated_at
    
    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm_with_frontend_compat(cls, obj):
        """Convert SQLAlchemy model to Pydantic with frontend compatibility"""
        data = {
            "id": obj.id,
            "name": obj.name,
            "description": obj.description,
            "vision": obj.vision,
            "problem_being_solved": obj.problem_being_solved,
            "status": obj.status,
            "progress": obj.progress,
            "charter": obj.charter,
            "created_at": obj.created_at,
            "updated_at": obj.updated_at,
            "owner_id": obj.owner_id,
            "lastUpdate": obj.updated_at.strftime("%d-%b-%Y") if obj.updated_at else ""
        }
        return cls(**data)

class ProjectListResponse(BaseModel):
    projects: List[ProjectResponse]
    total: int
    page: int
    size: int
    total_pages: int

# Charter validation schemas
class CharterValidationIssue(BaseModel):
    field: str
    issue: str
    suggestion: str
    
class CharterValidationResponse(BaseModel):
    is_valid: bool
    issues: List[CharterValidationIssue] = []
    improved_charter: Optional[Dict[str, Any]] = None
