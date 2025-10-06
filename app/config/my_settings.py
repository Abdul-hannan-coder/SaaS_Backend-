from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")

    # Other settings
    PORT: int = os.getenv("PORT")

    # GEMINI API KEY
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    
    # Google OAuth Settings
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")

    class Config:
        env_file = ".env"

settings = Settings() 