from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from src.handlers import routers
from src.database.config import get_db
from src.database.models import Task, Category

app = FastAPI()

# Include routers
for router in routers:
    app.include_router(router)

# Database health check
@app.get("/health/db")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Try to execute a simple query
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}
