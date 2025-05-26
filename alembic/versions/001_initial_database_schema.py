"""Initial database schema

Revision ID: 001
Revises: 
Create Date: 2025-05-25 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('full_name', sa.String(length=200), nullable=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_superuser', sa.Boolean(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Create projects table
    op.create_table('projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('vision', sa.Text(), nullable=True),
        sa.Column('problem_being_solved', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('DRAFT', 'IN_PLANNING', 'IN_DEVELOPMENT', 'IN_REVIEW', 'COMPLETED', 'ON_HOLD', 'CANCELLED', name='projectstatus'), nullable=False),
        sa.Column('progress', sa.Float(), nullable=False, default=0.0),
        sa.Column('charter', sa.JSON(), nullable=True),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_projects_id'), 'projects', ['id'], unique=False)

    # Create releases table
    op.create_table('releases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('version', sa.String(length=50), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('scope_modules', sa.JSON(), nullable=True),
        sa.Column('progress', sa.Float(), nullable=False, default=0.0),
        sa.Column('status', sa.Enum('NOT_STARTED', 'PLANNING', 'IN_PROGRESS', 'TESTING', 'COMPLETED', 'ON_HOLD', name='releasestatus'), nullable=False),
        sa.Column('goals', sa.JSON(), nullable=True),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_releases_id'), 'releases', ['id'], unique=False)

    # Create epics table
    op.create_table('epics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('version', sa.String(length=50), nullable=True),
        sa.Column('status', sa.Enum('DRAFT', 'READY', 'IN_PROGRESS', 'COMPLETED', 'ON_HOLD', name='epicstatus'), nullable=False),
        sa.Column('progress', sa.Float(), nullable=False, default=0.0),
        sa.Column('acceptance_criteria', sa.JSON(), nullable=True),
        sa.Column('business_value', sa.Text(), nullable=True),
        sa.Column('technical_notes', sa.Text(), nullable=True),
        sa.Column('architecture_notes', sa.Text(), nullable=True),
        sa.Column('release_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['release_id'], ['releases.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_epics_id'), 'epics', ['id'], unique=False)

    # Create user_stories table
    op.create_table('user_stories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('story_points', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('DRAFT', 'READY', 'IN_PROGRESS', 'IN_REVIEW', 'TESTING', 'COMPLETED', 'BLOCKED', name='storystatus'), nullable=False),
        sa.Column('priority', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='storypriority'), nullable=False),
        sa.Column('assignee_id', sa.Integer(), nullable=True),
        sa.Column('acceptance_criteria', sa.JSON(), nullable=True),
        sa.Column('business_value', sa.Text(), nullable=True),
        sa.Column('technical_notes', sa.Text(), nullable=True),
        sa.Column('architecture_recommendations', sa.JSON(), nullable=True),
        sa.Column('epic_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['assignee_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['epic_id'], ['epics.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_stories_id'), 'user_stories', ['id'], unique=False)

    # Create use_cases table
    op.create_table('use_cases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('preconditions', sa.JSON(), nullable=True),
        sa.Column('main_flow', sa.JSON(), nullable=True),
        sa.Column('alternative_flows', sa.JSON(), nullable=True),
        sa.Column('postconditions', sa.JSON(), nullable=True),
        sa.Column('primary_actor', sa.String(length=100), nullable=True),
        sa.Column('secondary_actors', sa.JSON(), nullable=True),
        sa.Column('user_story_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_story_id'], ['user_stories.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_use_cases_id'), 'use_cases', ['id'], unique=False)

    # Create test_cases table
    op.create_table('test_cases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('test_type', sa.String(length=50), nullable=True),
        sa.Column('preconditions', sa.JSON(), nullable=True),
        sa.Column('test_steps', sa.JSON(), nullable=True),
        sa.Column('expected_results', sa.JSON(), nullable=True),
        sa.Column('priority', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='storypriority'), nullable=False),
        sa.Column('automated', sa.String(length=10), nullable=False, default='No'),
        sa.Column('user_story_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_story_id'], ['user_stories.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_test_cases_id'), 'test_cases', ['id'], unique=False)

    # Create comments table
    op.create_table('comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('user_story_id', sa.Integer(), nullable=True),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['user_story_id'], ['user_stories.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comments_id'), 'comments', ['id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign key constraints)
    op.drop_table('comments')
    op.drop_table('test_cases')
    op.drop_table('use_cases')
    op.drop_table('user_stories')
    op.drop_table('epics')
    op.drop_table('releases')
    op.drop_table('projects')
    op.drop_table('users')
    
    # Drop enums
    sa.Enum(name='projectstatus').drop(op.get_bind())
    sa.Enum(name='releasestatus').drop(op.get_bind())
    sa.Enum(name='epicstatus').drop(op.get_bind())
    sa.Enum(name='storystatus').drop(op.get_bind())
    sa.Enum(name='storypriority').drop(op.get_bind())
