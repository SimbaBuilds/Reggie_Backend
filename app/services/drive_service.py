from app.core.config import settings
from googleapiclient.discovery import build
from app.utils.gsuite_utils import google_authenticate

def build_drive_service():
    creds = google_authenticate()
    return build('drive', 'v3', credentials=creds)
