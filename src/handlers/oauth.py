from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from src.database.config import get_db
from src.schemas.oauth import OAuth2AuthorizationResponse, OAuth2CallbackRequest
from src.schemas.user import Token
from src.services.google_oauth_service import GoogleOAuthService
from src.dependencies import get_auth_cache
from src.services.auth_cache import AuthCache

router = APIRouter(prefix="/auth/oauth", tags=["oauth"])


@router.get("/google/authorize", response_model=OAuth2AuthorizationResponse)
async def google_authorize():
    """Get Google OAuth2 authorization URL"""
    try:
        authorization_url = GoogleOAuthService.get_authorization_url()
        return OAuth2AuthorizationResponse(authorization_url=authorization_url)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate authorization URL: {str(e)}"
        )


@router.get("/google/callback")
async def google_callback(
    code: str,
    state: Optional[str] = None,
    db: Session = Depends(get_db),
    auth_cache: AuthCache = Depends(get_auth_cache)
):
    """Handle Google OAuth2 callback and authenticate user"""
    try:
        # Exchange authorization code for access token
        token_data = await GoogleOAuthService.exchange_code_for_token(code)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange authorization code for token"
            )
        
        # Get user information from Google
        access_token = token_data.get("access_token")
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token received from Google"
            )
        
        user_info = await GoogleOAuthService.get_user_info(str(access_token))
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user information from Google"
            )
        
        # Get or create user in database
        user = GoogleOAuthService.get_or_create_user(db, user_info)
        
        # Create JWT token for the user
        token_result = GoogleOAuthService.create_oauth_token(user)
        
        # Store token in cache
        auth_cache.store_auth_token(
            user_id=getattr(user, 'id'),
            token=token_result["access_token"],
            expiration_time=token_result["expires_in"]
        )
        
        # Return token response
        return Token(
            access_token=token_result["access_token"],
            token_type=token_result["token_type"],
            expires_in=token_result["expires_in"],
            user_id=token_result["user_id"]
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth2 authentication failed: {str(e)}"
        )


@router.post("/google/callback", response_model=Token)
async def google_callback_post(
    callback_data: OAuth2CallbackRequest,
    db: Session = Depends(get_db),
    auth_cache: AuthCache = Depends(get_auth_cache)
):
    """Handle Google OAuth2 callback via POST request"""
    try:
        # Exchange authorization code for access token
        token_data = await GoogleOAuthService.exchange_code_for_token(callback_data.code)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange authorization code for token"
            )
        
        # Get user information from Google
        access_token = token_data.get("access_token")
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token received from Google"
            )
        
        user_info = await GoogleOAuthService.get_user_info(str(access_token))
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user information from Google"
            )
        
        # Get or create user in database
        user = GoogleOAuthService.get_or_create_user(db, user_info)
        
        # Create JWT token for the user
        token_result = GoogleOAuthService.create_oauth_token(user)
        
        # Store token in cache
        auth_cache.store_auth_token(
            user_id=getattr(user, 'id'),
            token=token_result["access_token"],
            expiration_time=token_result["expires_in"]
        )
        
        # Return token response
        return Token(
            access_token=token_result["access_token"],
            token_type=token_result["token_type"],
            expires_in=token_result["expires_in"],
            user_id=token_result["user_id"]
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth2 authentication failed: {str(e)}"
        )
