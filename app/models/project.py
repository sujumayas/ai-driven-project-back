from sqlalchemy import Column, String, Text, Integer, Float, ForeignKey, Enum, JSON, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
import enum
from .base import BaseModel

class ProjectStatus(str, enum.Enum):
    DRAFT = "Draft"
    IN_PLANNING = "In Planning"
    IN_DEVELOPMENT = "In Development"
    IN_REVIEW = "In Review"
    COMPLETED = "Completed"
    ON_HOLD = "On Hold"
    CANCELLED = "Cancelled"

class ReleaseStatus(str, enum.Enum):
    NOT_STARTED = "Not Started"
    PLANNING = "Planning"
    IN_PROGRESS = "In Progress"
    TESTING = "Testing"
    COMPLETED = "Completed"
    ON_HOLD = "On Hold"

class EpicStatus(str, enum.Enum):
    DRAFT = "Draft"
    READY = "Ready"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    ON_HOLD = "On Hold"

class StoryStatus(str, enum.Enum):
    DRAFT = "Draft"
    READY = "Ready" 
    IN_PROGRESS = "In Progress"
    IN_REVIEW = "In Review"
    TESTING = "Testing"
    COMPLETED = "Completed"
    BLOCKED = "Blocked"

class StoryPriority(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class Project(BaseModel):
    __tablename__ = "projects"
    
    # Basic project information
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    vision = Column(Text, nullable=True)
    problem_being_solved = Column(Text, nullable=True)
    
    # Project status and progress
    status = Column(Enum(ProjectStatus), default=ProjectStatus.DRAFT, nullable=False)
    progress = Column(Float, default=0.0, nullable=False)  # 0-100 percentage
    
    # Project charter (JSON format)
    charter = Column(JSON, nullable=True)
    
    # Ownership
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    releases = relationship("Release", back_populates="project", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="project", cascade="all, delete-orphan")
    
    @hybrid_property
    def total_stories(self):
        """Get total number of user stories across all releases"""
        return sum(len(epic.user_stories) for release in self.releases for epic in release.epics)
    
    @hybrid_property
    def completed_stories(self):
        """Get number of completed user stories"""
        return sum(
            len([story for story in epic.user_stories if story.status == StoryStatus.COMPLETED])
            for release in self.releases
            for epic in release.epics
        )

class Release(BaseModel):
    __tablename__ = "releases"
    
    # Basic release information
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    version = Column(String(50), nullable=True)
    
    # Timeline
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    
    # Scope and progress
    scope_modules = Column(JSON, nullable=True)  # List of module names
    progress = Column(Float, default=0.0, nullable=False)  # 0-100 percentage
    status = Column(Enum(ReleaseStatus), default=ReleaseStatus.NOT_STARTED, nullable=False)
    
    # Goals and objectives
    goals = Column(JSON, nullable=True)  # List of release goals
    
    # Project relationship
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    project = relationship("Project", back_populates="releases")
    
    # Child relationships
    epics = relationship("Epic", back_populates="release", cascade="all, delete-orphan")

class Epic(BaseModel):
    __tablename__ = "epics"
    
    # Basic epic information
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    version = Column(String(50), nullable=True)
    
    # Status and priority
    status = Column(Enum(EpicStatus), default=EpicStatus.DRAFT, nullable=False)
    progress = Column(Float, default=0.0, nullable=False)  # 0-100 percentage
    
    # Epic scope and requirements
    acceptance_criteria = Column(JSON, nullable=True)  # List of criteria
    business_value = Column(Text, nullable=True)
    
    # Technical details
    technical_notes = Column(Text, nullable=True)
    architecture_notes = Column(Text, nullable=True)
    
    # Release relationship
    release_id = Column(Integer, ForeignKey("releases.id"), nullable=False)
    release = relationship("Release", back_populates="epics")
    
    # Child relationships
    user_stories = relationship("UserStory", back_populates="epic", cascade="all, delete-orphan")

class UserStory(BaseModel):
    __tablename__ = "user_stories"
    
    # Basic story information
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    story_points = Column(Integer, nullable=True)
    
    # Status and assignment
    status = Column(Enum(StoryStatus), default=StoryStatus.DRAFT, nullable=False)
    priority = Column(Enum(StoryPriority), default=StoryPriority.MEDIUM, nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Story details
    acceptance_criteria = Column(JSON, nullable=True)  # List of criteria
    business_value = Column(Text, nullable=True)
    
    # Technical details
    technical_notes = Column(Text, nullable=True)
    architecture_recommendations = Column(JSON, nullable=True)  # List of recommendations
    
    # Epic relationship
    epic_id = Column(Integer, ForeignKey("epics.id"), nullable=False)
    epic = relationship("Epic", back_populates="user_stories")
    
    # Assignment relationship
    assignee = relationship("User", back_populates="assigned_stories")
    
    # Child relationships
    use_cases = relationship("UseCase", back_populates="user_story", cascade="all, delete-orphan")
    test_cases = relationship("TestCase", back_populates="user_story", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user_story", cascade="all, delete-orphan")

class UseCase(BaseModel):
    __tablename__ = "use_cases"
    
    # Basic use case information
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Use case details
    preconditions = Column(JSON, nullable=True)  # List of preconditions
    main_flow = Column(JSON, nullable=True)  # List of steps
    alternative_flows = Column(JSON, nullable=True)  # List of alternative scenarios
    postconditions = Column(JSON, nullable=True)  # List of postconditions
    
    # Actor and system interaction
    primary_actor = Column(String(100), nullable=True)
    secondary_actors = Column(JSON, nullable=True)  # List of actors
    
    # User story relationship
    user_story_id = Column(Integer, ForeignKey("user_stories.id"), nullable=False)
    user_story = relationship("UserStory", back_populates="use_cases")

class TestCase(BaseModel):
    __tablename__ = "test_cases"
    
    # Basic test case information
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Test case details
    test_type = Column(String(50), nullable=True)  # unit, integration, e2e, etc.
    preconditions = Column(JSON, nullable=True)  # List of setup requirements
    test_steps = Column(JSON, nullable=True)  # List of test steps
    expected_results = Column(JSON, nullable=True)  # List of expected outcomes
    
    # Test execution
    priority = Column(Enum(StoryPriority), default=StoryPriority.MEDIUM, nullable=False)
    automated = Column(String(10), default="No", nullable=False)  # Yes/No/Partial
    
    # User story relationship
    user_story_id = Column(Integer, ForeignKey("user_stories.id"), nullable=False)
    user_story = relationship("UserStory", back_populates="test_cases")

class Comment(BaseModel):
    __tablename__ = "comments"
    
    # Comment content
    content = Column(Text, nullable=False)
    
    # Comment relationships (polymorphic - can belong to project, story, etc.)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    user_story_id = Column(Integer, ForeignKey("user_stories.id"), nullable=True)
    
    # Author relationship
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    author = relationship("User", back_populates="comments")
    
    # Parent relationships
    project = relationship("Project", back_populates="comments")
    user_story = relationship("UserStory", back_populates="comments")
