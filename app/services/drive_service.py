from app.core.config import settings
from googleapiclient.discovery import build

def build_drive_service():
    creds = authenticate()
    return build('drive', 'v3', credentials=creds)
