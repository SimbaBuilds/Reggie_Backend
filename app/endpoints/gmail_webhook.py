from fastapi import APIRouter, Request, HTTPException

from google.oauth2 import id_token
from google.auth.transport import requests
from app.schemas.gmail_webhook import PubsubMessage
import base64
import time
from sqlalchemy.orm import Session
import base64

router = APIRouter()





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

