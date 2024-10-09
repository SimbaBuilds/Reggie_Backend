import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Reggie Backend"
    PROJECT_VERSION: str = "1.0.0"
    ALLOWED_ORIGINS: list = ["http://localhost:3000"]  # Add your frontend URL here
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI")
    EMAIL_LABEL_NAMES: list = ["Cumulative Files", "Miscellaneous Labeled Records", "Miscellaneous Unlabeled Records",  "Records Requests", "Template Response"]

    class Config:
        env_file = ".env"

settings = Settings()