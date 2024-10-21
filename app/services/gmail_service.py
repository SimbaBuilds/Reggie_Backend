from googleapiclient.discovery import build
from app.core.config import settings



def build_gmail_service():
    creds = authenticate()
    return build('gmail', 'v1', credentials=creds)