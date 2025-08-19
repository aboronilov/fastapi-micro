from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GOOGLE_TOKEN: str = Field(default="", description="Google API token")
    GOOGLE_CLIENT_ID: str = Field(default="", description="Google client ID")
    
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