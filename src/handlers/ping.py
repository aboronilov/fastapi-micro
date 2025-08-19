from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.database.config import get_db

router = APIRouter(prefix="/ping", tags=["ping"])

@router.get("/app")
async def ping_app():
    """Application health check"""
    return {"message": "pong", "status": "healthy"}

@router.get("/db")
async def ping_db(db: Session = Depends(get_db)):
    """Database health check"""
    try:
        # Try to execute a simple query
        db.execute(text("SELECT 1"))
        return {"message": "pong", "database": "connected", "status": "healthy"}
    except Exception as e:
        return {"message": "error", "database": "disconnected", "status": "unhealthy", "error": str(e)}