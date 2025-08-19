from .config import Base, engine, get_db

# Import all models here for Alembic to detect them
__all__ = ["Base", "engine", "get_db"]

def create_tables():
    """Create all tables in the database"""
    # Import models here to avoid circular imports
    from .models import Task, Category
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """Drop all tables in the database"""
    # Import models here to avoid circular imports
    from .models import Task, Category
    Base.metadata.drop_all(bind=engine)
