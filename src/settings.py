from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Google OAuth2 Configuration
    GOOGLE_CLIENT_ID: str = Field(default="", description="Google OAuth2 client ID")
    GOOGLE_CLIENT_SECRET: str = Field(default="", description="Google OAuth2 client secret")
    GOOGLE_REDIRECT_URI: str = Field(default="http://localhost:8000/auth/google/callback", description="Google OAuth2 redirect URI")
    
    # JWT Configuration
    JWT_SECRET_KEY: str = Field(default="your-secret-key", description="JWT secret key")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Access token expiration time in minutes")
    
    # Cache configuration
    CACHE_EXPIRATION_SECONDS: int = Field(
        default=300, 
        description="Cache expiration time in seconds (default: 5 minutes)"
    )

    class Config:
        env_file = "env"

try:
    settings = Settings()
except Exception as e:
    print(f"Error loading settings: {e}")
    settings = None