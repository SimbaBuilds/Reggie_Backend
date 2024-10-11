from fastapi import APIRouter, Request, Depends
from app.utils.gmail_utils import get_label_id
from app.core.config import settings
from app.db.session import get_db
from app.utils.thread_store import is_thread_id_stored, remove_thread_info
from app.services.gmail_service import build_gmail_service

from sqlalchemy.orm import Session
import base64

router = APIRouter()


def handle_watched_label(service, user_id, history_id, label_id, db):
    pass

@router.post("/gmail")
async def gmail_webhook(request: Request, db: Session = Depends(get_db)):
    data = await request.json()

    if 'message' in data:
        pubsub_message = data['message']
        message_data = base64.urlsafe_b64decode(pubsub_message['data']).decode('utf-8')
        attributes = pubsub_message.get('attributes', {})
        history_id = attributes.get('historyId')

        service = build_gmail_service()
        user_id = 'me'

        for label_name in settings.EMAIL_LABEL_NAMES:
            label_id = get_label_id(service, label_name)
            thread_id = await handle_watched_label(service, user_id, history_id, label_id, db)
            
            if thread_id and is_thread_id_stored(thread_id):
                # Process the user's response here
                # You can add your logic to extract student information from the email
                # and update your records accordingly
                
                # After processing, remove the thread_id from storage
                remove_thread_info(thread_id)

    return {"status": "success"}