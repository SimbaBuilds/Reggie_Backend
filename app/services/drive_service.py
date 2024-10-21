from app.core.config import settings
from googleapiclient.discovery import build
from app.utils.google_auth import authenticate

def build_drive_service():
    creds = authenticate()
    return build('drive', 'v3', credentials=creds)
