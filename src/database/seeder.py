from sqlalchemy.orm import Session
from .models import Category, Task

def seed_database(db: Session):
    """Seed the database with initial data"""
    
    # Create categories
    categories = [
        Category(name="Work", description="Work-related tasks"),
        Category(name="Personal", description="Personal tasks"),
        Category(name="Study", description="Study and learning tasks"),
    ]
    
    for category in categories:
        db.add(category)
    db.commit()
    
    # Create tasks
    tasks = [
        Task(
            name="Learn FastAPI",
            description="Study FastAPI framework",
            pomodoro_count=4,
            category_id=categories[2].id,  # Study category
            completed=False
        ),
        Task(
            name="Build microservice",
            description="Create a microservice with FastAPI",
            pomodoro_count=8,
            category_id=categories[0].id,  # Work category
            completed=False
        ),
        Task(
            name="Write tests",
            description="Add unit tests for the API",
            pomodoro_count=6,
            category_id=categories[0].id,  # Work category
            completed=False
        ),
        Task(
            name="Exercise",
            description="Daily workout routine",
            pomodoro_count=2,
            category_id=categories[1].id,  # Personal category
            completed=True
        ),
    ]
    
    for task in tasks:
        db.add(task)
    db.commit()
    
    print("Database seeded successfully!")
