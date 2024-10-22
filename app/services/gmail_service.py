from googleapiclient.discovery import build
from app.core.config import settings
from app.utils.gsuite_utils import google_authenticate  


def build_gmail_service():
    creds = google_authenticate()
    return build('gmail', 'v1', credentials=creds)