import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings."""
    SUPABASE_URL: str
    SUPABASE_KEY: str
    CLERK_API_SECRET_KEY: str
    CLERK_API_PUBLIC_KEY: str
    CLERK_WEBHOOK_SECRET: str = ""
    AI_MODEL: str
    GEMINI_API_KEY: str
    BOX_CLIENT_ID: str
    BOX_CLIENT_SECRET: str
    PINECONE_API_KEY: str 
    GENAI_KEY: str
    PINECONE_ENVIRONMENT: str
    E2B_API_KEY: str

    
    class Config:
        env_file = ".env"

# Create settings instance
settings = Settings()