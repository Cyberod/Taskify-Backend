import os
from pydantic import BaseSettings
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Define the base directory
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "Taskify"
    API_V1: str = "/api/v1"

    # Database settings
    DB_URL: str = os.getenv("DB_URL", "postgresql://postgres:postgres@localhost/5432/taskify")

    # JWT settings
    JWT_SECRET_KEY: str = os.getenv("SECRET_KEY", "your_jwt_secret_key_for_development")
    JWT_ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    JWT_EXPIRATION: int = 3 * 24 * 60  # in 3 days

    # CORS settings
    BACKEND_CORS_ORIGINS: list = ["*"]  # Allows all origins, In production i will change to specific domains


settings = Settings()
