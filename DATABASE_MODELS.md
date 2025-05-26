# Database Models - AI-Driven Project Flow

This document describes the database schema and models for the AI-Driven Project Flow backend.

## Database Schema Overview

The database consists of 8 main tables with the following relationships:

```
User (1) ←→ (N) Project
Project (1) ←→ (N) Release  
Release (1) ←→ (N) Epic
Epic (1) ←→ (N) UserStory
UserStory (1) ←→ (N) UseCase
UserStory (1) ←→ (N) TestCase  
UserStory (1) ←→ (N) Comment
User (1) ←→ (N) UserStory (assignee)
```

## Models

### User
- **Purpose**: Authentication and user management
- **Key Fields**: email, username, full_name, hashed_password, profile info
- **Relationships**: owns projects, assigned to stories, authors comments

### Project  
- **Purpose**: Main project container
- **Key Fields**: name, description, vision, problem_being_solved, status, progress, charter (JSON)
- **Relationships**: belongs to user, contains releases and comments

### Release
- **Purpose**: Project phases with timelines
- **Key Fields**: name, version, start/end dates, scope_modules (JSON), progress, goals (JSON)
- **Relationships**: belongs to project, contains epics

### Epic
- **Purpose**: Feature groupings within releases  
- **Key Fields**: name, description, version, status, acceptance_criteria (JSON), business_value
- **Relationships**: belongs to release, contains user stories

### UserStory
- **Purpose**: Detailed requirements within epics
- **Key Fields**: name, description, story_points, status, priority, acceptance_criteria (JSON)
- **Relationships**: belongs to epic, assigned to user, contains use cases and test cases

### UseCase
- **Purpose**: Detailed scenarios for user stories
- **Key Fields**: title, description, preconditions/main_flow/alternative_flows/postconditions (JSON)
- **Relationships**: belongs to user story

### TestCase
- **Purpose**: Testing scenarios for user stories
- **Key Fields**: title, description, test_type, test_steps (JSON), expected_results (JSON)
- **Relationships**: belongs to user story

### Comment
- **Purpose**: Collaboration and discussions
- **Key Fields**: content, polymorphic relationships (project_id, user_story_id)
- **Relationships**: belongs to user (author), belongs to project or user story

## Status Enums

- **ProjectStatus**: Draft, In Planning, In Development, In Review, Completed, On Hold, Cancelled
- **ReleaseStatus**: Not Started, Planning, In Progress, Testing, Completed, On Hold  
- **EpicStatus**: Draft, Ready, In Progress, Completed, On Hold
- **StoryStatus**: Draft, Ready, In Progress, In Review, Testing, Completed, Blocked
- **StoryPriority**: Low, Medium, High, Critical

## Setup Instructions

### 1. Database Setup

Make sure PostgreSQL is running with the configured settings:

```bash
# Default configuration (update in .env file)
DATABASE_URL=postgresql://username:password@localhost:5433/ai_project_flow
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Initialize Database

#### Option A: Using the Initialization Script (Recommended)
```bash
# Run the interactive initialization script
python scripts/init_db.py
```

This script will:
- Test database connection
- Create all tables 
- Optionally seed sample data for development

#### Option B: Using Alembic Migrations
```bash
# Initialize Alembic (if not already done)
alembic init alembic

# Run migrations to create tables
alembic upgrade head
```

### 4. Verify Setup

Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

Access the API documentation at `http://localhost:8000/docs` to verify the setup.

## Development Workflow

### Making Schema Changes

1. **Modify Models**: Update the SQLAlchemy models in `app/models/`
2. **Generate Migration**: 
   ```bash
   alembic revision --autogenerate -m "Description of changes"
   ```
3. **Review Migration**: Check the generated migration file in `alembic/versions/`
4. **Apply Migration**: 
   ```bash
   alembic upgrade head
   ```

### Sample Data

The initialization script creates sample data including:
- Demo user account (demo@aiprojectflow.com / demo123!)
- Sample project "Commerce Revolution"
- 2 releases with different statuses
- 2 epics with acceptance criteria
- 2 user stories with detailed information

This data matches the structure used in the frontend mock data for seamless integration.

## Key Features

### JSON Fields
Several models use JSON fields for flexible data storage:
- **Project.charter**: Complete project charter information
- **Release.scope_modules**: List of modules in scope
- **Epic.acceptance_criteria**: List of criteria
- **UserStory.architecture_recommendations**: List of technical recommendations

### Audit Trail
All models include:
- `created_at`: Automatic timestamp on creation
- `updated_at`: Automatic timestamp on updates
- Relationships to track ownership and assignment

### Hybrid Properties
Models include computed properties:
- `Project.total_stories`: Count of all stories across releases
- `Project.completed_stories`: Count of completed stories

## Integration with Frontend

The database models are designed to match the TypeScript interfaces used in the React frontend:

```typescript
// Frontend interface matches database model
interface Project {
  id: number;
  name: string;
  description: string;
  vision: string;
  problem_being_solved: string;
  status: "Draft" | "In Planning" | "In Development" | "In Review";
  progress: number;
  lastUpdate: string; // mapped from updated_at
}
```

This ensures seamless data flow between the database and UI components.
