import base64
from email.mime.text import MIMEText
from app.utils.handle_misc_records import get_label_id
from app.core.config import settings
from typing import Any, Dict
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os

# Function to handle OAuth authentication
def google_authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', settings.SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', settings.SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    print("authentication completed")
    return creds

def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return message


def get_email_body(email_data):
    parts = email_data['payload'].get('parts', [])
    
    for part in parts:
        if part['mimeType'] == 'text/plain':  # Check for plain text email part
            body = part['body']['data']
            decoded_body = base64.urlsafe_b64decode(body).decode('utf-8')
            return decoded_body
    
    return None


def start_watch(service, label_name):
    label_id = get_label_id(service, label_name)
    if not label_id:
        print(f"Label '{label_name}' not found")
        return None

    request_body = {
        'labelIds': [label_id],
        'topicName': settings.PUBSUB_TOPIC
    }

    try:
        response = service.users().watch(userId='me', body=request_body).execute()
        print(f"Watch started successfully for label '{label_name}'")
        return response
    except Exception as e:
        print(f"Error starting watch for label '{label_name}': {str(e)}")
        return None



def get_user_response(service, user_id, history_id, thread_id):
    # Fetch messages added since the last known historyId
    response = service.users().history().list(
        userId=user_id, startHistoryId=history_id, historyTypes=['messageAdded']
    ).execute()

    messages = []
    
    if 'history' in response:
        for history_record in response['history']:
            if 'messagesAdded' in history_record:
                for message in history_record['messagesAdded']:
                    message_id = message['message']['id']
                    message_data = service.users().messages().get(userId=user_id, id=message_id).execute()
                    
                    # Check if the message belongs to the same thread
                    if message_data['threadId'] == thread_id:
                        # Extract the message body
                        email_body = get_email_body(message_data)
                        print(f"User response found: {email_body}")
                        messages.append(email_body)
    
    if not messages:
        print("No user response found in this thread.")
        return None
    
    # Return the latest reply found in the same thread
    return messages[-1]


def get_sender_email(message):
    headers = message.get('payload', {}).get('headers', [])
    for header in headers:
        if header['name'].lower() == 'from':
            return header['value']
    return None

def get_subject(message):
    headers = message.get('payload', {}).get('headers', [])
    for header in headers:
        if header['name'].lower() == 'subject':
            return header['value']
    return 'No Subject'

def send_reply(service, user_id, original_message, reply_text, pdf_path=None):
    alias_email = 'reggie@flagarts.com'  # Your alias email
    recipient_email = get_sender_email(original_message)
    subject = get_subject(original_message)
    thread_id = original_message['threadId']
    message_id = original_message['id']

    message = create_message(alias_email, recipient_email, subject, reply_text)
    message['In-Reply-To'] = message_id
    message['References'] = message_id

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    body = {'raw': raw_message, 'threadId': thread_id}

    return service.users().messages().send(userId=user_id, body=body).execute()


def start_watch_for_labels(service, label_names):
    for label_name in label_names:
        start_watch(service, label_name)

def fetch_unread_with_label(label_id: str, gmail_service: Any, page_token: str) -> Dict[str, Any]:
    """
    Fetch unread messages with a specific label from Gmail.

    Args:
        label_id (str): The ID of the label to filter messages.
        gmail_service (Any): The Gmail service object.
        page_token (str): The page token for pagination.

    Returns:
        Dict[str, Any]: The response from the Gmail API containing the list of messages.
    """
    response = gmail_service.users().messages().list(
        userId='me', 
        labelIds=[label_id, 'UNREAD'],
        pageToken=page_token
    ).execute()

    return response