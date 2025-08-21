from pydantic import BaseModel
from typing import Optional


class OAuth2AuthorizationResponse(BaseModel):
    """Response model for OAuth2 authorization URL"""
    authorization_url: str
    message: str = "Redirect user to this URL to authorize with Google"


class OAuth2CallbackRequest(BaseModel):
    """Request model for OAuth2 callback"""
    code: str
    state: Optional[str] = None


class OAuth2UserInfo(BaseModel):
    """Model for OAuth2 user information"""
    id: str
    email: str
    name: str
    picture: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    locale: Optional[str] = None
