import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings."""
    SUPABASE_URL: str
    SUPABASE_KEY: str
    CLERK_API_SECRET_KEY: str
    CLERK_API_PUBLIC_KEY: str
    CLERK_WEBHOOK_SECRET: str = ""
    
    class Config:
        env_file = ".env"

# Create settings instance
settings = Settings()