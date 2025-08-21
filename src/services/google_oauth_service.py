import httpx
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from src.database.models import User
from src.utils.security import create_access_token
from src.settings import settings
import bcrypt


class GoogleOAuthService:
    """Service for handling Google OAuth2 authentication"""
    
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    @staticmethod
    def get_authorization_url() -> str:
        """Generate Google OAuth2 authorization URL"""
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "scope": "openid email profile",
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent"
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"https://accounts.google.com/o/oauth2/v2/auth?{query_string}"
    
    @staticmethod
    async def exchange_code_for_token(code: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for access token"""
        async with httpx.AsyncClient() as client:
            data = {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.GOOGLE_REDIRECT_URI
            }
            
            response = await client.post(GoogleOAuthService.GOOGLE_TOKEN_URL, data=data)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Token exchange failed: {response.text}")
                return None
    
    @staticmethod
    async def get_user_info(access_token: str) -> Optional[Dict[str, Any]]:
        """Get user information from Google using access token"""
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = await client.get(GoogleOAuthService.GOOGLE_USERINFO_URL, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"User info fetch failed: {response.text}")
                return None
    
    @staticmethod
    def get_or_create_user(db: Session, google_user_info: Dict[str, Any]) -> User:
        """Get existing user or create new user from Google OAuth2 data"""
        google_id = google_user_info.get("id")
        email = google_user_info.get("email")
        
        if not google_id or not email:
            raise ValueError("Invalid Google user info")
        
        # Check if user exists by Google ID
        user = db.query(User).filter(User.google_id == google_id).first()
        
        if user:
            return user
        
        # Check if user exists by email
        user = db.query(User).filter(User.email == email).first()
        
        if user:
            # Update existing user with Google ID
            user.google_id = google_id
            user.is_oauth_user = True  # type: ignore[attr-defined]
            avatar_url = google_user_info.get("picture")
            if avatar_url is not None:
                user.avatar_url = avatar_url  # type: ignore[attr-defined]
            username = google_user_info.get("name") or email.split("@")[0]
            if not getattr(user, "username", None):
                user.username = username  # type: ignore[attr-defined]
            db.commit()
            return user
        
        # Create new user
        new_user = User(
            email=email,
            username=google_user_info.get("name", email.split("@")[0]),
            google_id=google_id,
            avatar_url=google_user_info.get("picture"),
            is_oauth_user=True,
            password=None  # OAuth2 users don't have passwords
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user
    
    @staticmethod
    def create_oauth_token(user: User) -> Dict[str, Any]:
        """Create JWT token for OAuth2 user"""
        access_token_expires = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        from datetime import timedelta

        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=access_token_expires)
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": access_token_expires * 60,  # Convert to seconds
            "user_id": user.id
        }
