from fastapi import APIRouter, Request, HTTPException
from google.auth.transport import requests as google_requests
import base64
from google.oauth2 import id_token
try:
    from utils.gmail_utils import get_email_body, pass_to_gpt4omini, get_label_id, handle_watched_label, build_gmail_service, handle_misc_records
    from utils.handle_misc_records import email_label_names 
except ModuleNotFoundError:
    from app.utils.gmail_utils import get_email_body, pass_to_gpt4omini, get_label_id, handle_watched_label, build_gmail_service, handle_misc_records
    from app.utils.handle_misc_records import email_label_names

router = APIRouter()


# Function to verify the token from Google Pub/Sub
def verify_google_token(token):
    try:
        req = google_requests.Request()
        id_info = id_token.verify_oauth2_token(token, req)
        return True
    except Exception as e:
        print(f"Token verification failed: {e}")
        return False

# Example function to build the Gmail API service (use OAuth2 credentials)
def build_gmail_service():
    # Add your authentication logic here (OAuth2 flow)
    return None  # Return an authenticated Gmail service instance

# Fetch new emails from Gmail using the historyId from the Pub/Sub message
async def fetch_emails_from_history(service, user_id, history_id):
    history = service.users().history().list(userId=user_id, startHistoryId=history_id).execute()
    if 'history' in history:
        for record in history['history']:
            if 'messagesAdded' in record:
                for message_data in record['messagesAdded']:
                    message_id = message_data['message']['id']
                    email_data = service.users().messages().get(userId=user_id, id=message_id).execute()
                    process_received_email(email_data)

# Process the received email (similar to your original function)
def process_received_email(email_data):
    email_body = get_email_body(email_data)
    print(f"Received email: {email_body}")
    # Handle the email (reply, process data, etc.)


def is_reply_to_thread(message, thread_id):
    return message.get('threadId') == thread_id


def process_user_reply(message):
    email_body = get_email_body(message)
    listified_student = pass_to_gpt4omini(email_body)
    # Take further action with listified_student


def handle_watched_label(service, user_id, history_id, label_id):
    response = service.users().history().list(
        userId=user_id,
        startHistoryId=history_id,
        labelId=label_id,
        historyTypes=['messageAdded']
    ).execute()

    if 'history' in response:
        for history_record in response['history']:
            if 'messagesAdded' in history_record:
                for message_added in history_record['messagesAdded']:
                    message_id = message_added['message']['id']
                    message = service.users().messages().get(userId=user_id, id=message_id, format='full').execute()
                    
                    # Process the message based on the label
                    if label_id == get_label_id(service, "Miscellaneous Student Records"):
                        handle_misc_records(service, message)
                    elif label_id == get_label_id(service, "Student Cumulative Files"):
                        handle_misc_records(service, message)


@router.post("/webhook")
async def gmail_webhook(request: Request):
    data = await request.json()

    if 'message' in data:
        pubsub_message = data['message']
        message_data = base64.urlsafe_b64decode(pubsub_message['data']).decode('utf-8')
        attributes = pubsub_message.get('attributes', {})
        history_id = attributes.get('historyId')

        service = build_gmail_service()
        user_id = 'me'

        for label_name in email_label_names:
            label_id = get_label_id(service, label_name)
            handle_watched_label(service, user_id, history_id, label_id)

    return {"status": "success"}