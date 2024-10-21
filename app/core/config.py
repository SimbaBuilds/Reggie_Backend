import os
from pydantic_settings import BaseSettings
from pydantic import Field
import ast
import json

class Settings(BaseSettings):
    PROJECT_NAME: str = "Reggie Backend"
    PROJECT_VERSION: str = "1.0.0"
    ALLOWED_ORIGINS: list = ["http://localhost:3000"]  # Add your frontend URL here
    EMAIL_LABEL_NAMES: list = ["Cumulative Files", "Miscellaneous Labeled Records", "Miscellaneous Unlabeled Records",  "Records Requests", "Template Response"]
    SCOPES: list = ['https://www.googleapis.com/auth/gmail.modify', 'https://www.googleapis.com/auth/gmail.compose', 'https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']


    # Sensitive information should be loaded from environment variables
    SUPABASE_PROJECT: str = Field(..., env="SUPABASE_PROJECT")
    SUPABASE_PASSWORD: str = Field(..., env="SUPABASE_PASSWORD")
    SUPABASE_ACCESS_TOKEN: str = Field(..., env="SUPABASE_ACCESS_TOKEN")
    SUPABASE_URL: str = Field(..., env="SUPABASE_URL")
    SUPABASE_KEY: str = Field(..., env="SUPABASE_KEY")
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    PUBSUB_TOPIC: str = Field(..., env="PUBSUB_TOPIC")
    PUBSUB_PROJECT_ID: str = Field(..., env="PUBSUB_PROJECT_ID")
    PUBSUB_SUBSCRIPTION: str = Field(..., env="PUBSUB_SUBSCRIPTION")
    PUBSUB_ACCESS: dict = Field(..., env="PUBSUB_ACCESS")    
    NGROK_URL: str = Field(..., env="NGROK_URL")
    NGROK_AUTH_TOKEN: str = Field(..., env="NGROK_AUTH_TOKEN")
    JWT_SECRET: str = Field(..., env="JWT_SECRET")
    ALGORITHM: str  = Field(..., env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(..., env="ACCESS_TOKEN_EXPIRE_MINUTES")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str):
            if field_name == "PUBSUB_ACCESS":
                return json.loads(raw_val)
            return raw_val

settings = Settings()

# Ensure PUBSUB_ACCESS is a dictionary
if isinstance(settings.PUBSUB_ACCESS, str):
    try:
        settings.PUBSUB_ACCESS = json.loads(settings.PUBSUB_ACCESS)
    except json.JSONDecodeError:
        try:
            settings.PUBSUB_ACCESS = ast.literal_eval(settings.PUBSUB_ACCESS)
        except (ValueError, SyntaxError):
            raise ValueError(f"Invalid format for PUBSUB_ACCESS: {settings.PUBSUB_ACCESS}")
