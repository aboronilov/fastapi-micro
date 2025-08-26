"""Add sample data

Revision ID: 002
Revises: 001
Create Date: 2024-01-01 00:01:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_add_sample_data'
down_revision = '001_initial_migration'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Insert sample categories
    op.execute("""
        INSERT INTO categories (name, description) VALUES 
        ('Work', 'Work-related tasks'),
        ('Personal', 'Personal tasks'),
        ('Study', 'Study and learning tasks')
    """)
    
    # Insert sample tasks
    op.execute("""
        INSERT INTO tasks (name, description, pomodoro_count, category_id, completed) VALUES 
        ('Learn FastAPI', 'Study FastAPI framework', 4, 3, false),
        ('Build microservice', 'Create a microservice with FastAPI', 8, 1, false),
        ('Write tests', 'Add unit tests for the API', 6, 1, false),
        ('Exercise', 'Daily workout routine', 2, 2, true)
    """)


def downgrade() -> None:
    # Remove sample data
    op.execute("DELETE FROM tasks")
    op.execute("DELETE FROM categories")
