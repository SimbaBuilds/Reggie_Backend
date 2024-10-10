import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Reggie Backend"
    PROJECT_VERSION: str = "1.0.0"
    ALLOWED_ORIGINS: list = ["http://localhost:3000"]  # Add your frontend URL here
    EMAIL_LABEL_NAMES: list = ["Cumulative Files", "Miscellaneous Labeled Records", "Miscellaneous Unlabeled Records",  "Records Requests", "Template Response"]
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify', 'https://www.googleapis.com/auth/gmail.compose', 'https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
    ROSTER_FILE_PATH: str = "ESD.csv"
    SUPABASE_PROJECT = "REGGIE"
    SUPABASE_PASSWORD = "6G0Khs9gR5JLEOQx"
    SUPABASE_ACCESS_TOKEN = "sbp_7090ce12b0e59f1ec3261546bb7d53d44fc2cc95"
    SUPABASE_URL = "https://zulljpjbydipolysecbp.supabase.co"
    SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp1bGxqcGpieWRpcG9seXNlY2JwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mjg1MjgwMjEsImV4cCI6MjA0NDEwNDAyMX0.p9JWiLiTU1RG9kpq3-okr60jK96ogEi9FZAypBuHur8"
            

    class Config:
        env_file = ".env"

settings = Settings()