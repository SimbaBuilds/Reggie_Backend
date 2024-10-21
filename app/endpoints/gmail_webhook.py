from fastapi import APIRouter, Request, Depends, HTTPException
from app.utils.gsuite_utils import get_label_id
from app.core.config import settings
from app.db.session import get_db
from app.utils.thread_store import is_thread_id_stored, remove_thread_info
from app.services.gmail_service import build_gmail_service
from google.auth import jwt
from google.oauth2 import id_token
from google.auth.transport import requests
from app.schemas.gmail_webhook import PubsubMessage
import base64
import time
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


@router.post("/api/gmail-webhook")
async def gmail_webhook(request: Request):
    payload = await request.json()
    print(f"Received webhook payload: {payload}")
    return {"status": "success"}


@router.post("/api/gmail-webhook")
async def gmail_webhook(request: Request, pubsub_message: PubsubMessage):
    # Verify the request (optional but recommended)
    try:
        # Get the Cloud Pub/Sub-generated JWT in the "Authorization" header.
        bearer_token = request.headers.get('Authorization')
        if not bearer_token:
            raise HTTPException(status_code=400, detail="Authorization header missing")
        
        token = bearer_token.split(' ')[1]

        # Verify and decode the JWT using the Cloud Pub/Sub public key.
        claim = id_token.verify_oauth2_token(
            token, requests.Request(), audience='Reggie')

        # Check that the token is not expired.
        if claim['exp'] < int(time.time()):
            raise HTTPException(status_code=400, detail="Token expired")

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid token: {str(e)}")

    # Extract the message data
    message = pubsub_message.message
    if 'data' in message:
        event_data = base64.b64decode(message['data']).decode('utf-8')
        # Process the event data here
        print(f"Received event data: {event_data}")

    return {"success": True}

