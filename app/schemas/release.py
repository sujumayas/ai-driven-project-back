from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


class ReleaseStatus(str, Enum):
    NOT_STARTED = "Not Started"
    PLANNING = "Planning"
    IN_PROGRESS = "In Progress"
    TESTING = "Testing"
    COMPLETED = "Completed"
    ON_HOLD = "On Hold"


# Request schemas
class ReleaseCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Release name")
    description: Optional[str] = Field(None, description="Release description")
    version: Optional[str] = Field(None, max_length=50, description="Release version")
    start_date: Optional[date] = Field(None, description="Release start date")
    end_date: Optional[date] = Field(None, description="Release end date")
    scope_modules: Optional[List[str]] = Field(
        default=[], description="Module names in scope"
    )
    goals: Optional[List[str]] = Field(default=[], description="Release goals")


class ReleaseUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    version: Optional[str] = Field(None, max_length=50)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    scope_modules: Optional[List[str]] = None
    goals: Optional[List[str]] = None
    status: Optional[ReleaseStatus] = None
    progress: Optional[float] = Field(None, ge=0, le=100)


# Response schemas
class ReleaseResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    version: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    scope_modules: List[str]
    goals: List[str]
    status: ReleaseStatus
    progress: float
    project_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReleaseListResponse(BaseModel):
    releases: List[ReleaseResponse]
    total: int


# Release extraction schemas
class ExtractedReleaseData(BaseModel):
    name: str
    description: str
    version: Optional[str] = None
    start_date: Optional[str] = None  # YYYY-MM-DD format
    end_date: Optional[str] = None  # YYYY-MM-DD format
    scope_modules: List[str] = []
    goals: List[str] = []
    status: str = "Not Started"
    dependencies: List[str] = []
    risks: List[str] = []
    estimated_effort: Optional[str] = None


class ExtractionRecommendation(BaseModel):
    type: str = Field(..., description="Type: scope|timeline|dependencies|risk")
    message: str
    priority: str = Field(..., description="Priority: low|medium|high")


class ReleaseStrategy(BaseModel):
    total_releases: int
    overall_timeline: str
    release_cadence: str
    critical_path: List[str]


class ReleaseExtractionRequest(BaseModel):
    project_id: int


class ReleaseExtractionResponse(BaseModel):
    extracted_releases: List[ExtractedReleaseData]
    recommendations: List[ExtractionRecommendation]
    release_strategy: ReleaseStrategy
    success: bool = True
    message: Optional[str] = None


class ReleaseCreationFromExtractionRequest(BaseModel):
    project_id: int
    selected_releases: List[int] = Field(
        ..., description="Indices of releases to create"
    )
    extracted_data: ReleaseExtractionResponse


class BulkReleaseCreationResponse(BaseModel):
    created_releases: List[ReleaseResponse]
    failed_releases: List[Dict[str, Any]] = []
    success_count: int
    total_count: int
