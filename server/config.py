import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings."""
    SUPABASE_URL: str
    SUPABASE_KEY: str
    
    class Config:
        env_file = ".env"

# Create settings instance
settings = Settings()