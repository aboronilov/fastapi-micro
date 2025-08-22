from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.database.config import get_db
from src.schemas.user import UserCreate, UserLogin, UserResponse, Token
from src.services.auth_service import AuthService
from src.services.auth_cache import AuthCache
from src.dependencies import get_auth_service, get_auth_cache

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Token)
async def login(
    user_credentials: UserLogin,
    db: Session = Depends(get_db),
    auth_service: type = Depends(get_auth_service),
    auth_cache: AuthCache = Depends(get_auth_cache)
):
    """Login user with username and password"""
    result = await auth_service.login(db, user_credentials.username, user_credentials.password, auth_cache)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    return Token(
        access_token=result["access_token"],
        token_type=result["token_type"],
        expires_in=result["expires_in"],
        user_id=result["user_id"]
    )

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user: UserCreate,
    db: Session = Depends(get_db),
    auth_service: type = Depends(get_auth_service)
):
    """Register a new user"""
    try:
        new_user = await auth_service.register(db, user)
        return new_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.get("/cache/info")
async def get_auth_cache_info(
    auth_cache: AuthCache = Depends(get_auth_cache)
):
    """Get auth cache information including TTL and statistics"""
    return auth_cache.get_cache_info()


@router.delete("/cache/clear")
async def clear_auth_cache(
    auth_cache: AuthCache = Depends(get_auth_cache)
):
    """Manually clear the auth cache (for testing or emergency use)"""
    auth_cache.clear_auth_cache()
    return {"message": "Auth cache cleared successfully"}
