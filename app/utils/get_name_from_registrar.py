
import requests
import re
from email.mime.text import MIMEText
import base64
from fastapi import FastAPI, Request, HTTPException
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from googleapiclient.discovery import build
from pydantic import BaseModel
from email.mime.text import MIMEText
try:    
    from utils.gmail_utils import get_user_response, send_reply, start_watch
    from utils.thread_store import store_thread_info
except ModuleNotFoundError:
    from app.utils.gmail_utils import get_user_response, send_reply, start_watch
    from app.utils.thread_store import store_thread_info
import os

api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    raise ValueError("No API key found. Please set the OPENAI_API_KEY environment variable.")




def pass_to_gpt4omini(email_message:str):
    prompt = f"""
    Extract the student last name, first name, and date of birth from this email response:{email_message}.  
    The user is asked to provide the student last name, first name and date of birth in the format last, first, DOB.
    Output in the format lastname_firstname_mm/dd/year delimitted by triple backticks.
    Make sure single digit months and days are formatted as 0X.
    """


    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
    }

    payload = {
    "model": "gpt-4o",
    "messages": [
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": prompt
            },
        ]
        }
    ],
    "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response_json = response.json()  # Convert the response to a dictionary
    content = response_json['choices'][0]['message']['content']


    try:
        parsed_text = re.search(r'```(.*?)```', content, re.DOTALL).group(1).strip()
    except AttributeError:
        parsed_text = None  # or handle the error in another appropriate way

    if parsed_text is None:
        print("No text found in email")
        return ['', '', '']

    listified_student = parsed_text.split('_')

    return listified_student

# This could be a simple in-memory store or a database
stored_thread_ids = set()

def store_thread_info(thread_id, history_id):
    stored_thread_ids.add(thread_id)
    # Optionally store other details like history_id if needed


def get_name_from_registrar(pdf_path, creds, gmail_service, message, label_name):  
    thread_id = message['threadId']
    history_id = message['historyId']
    
    reply_message = "To whom does this record belong? Please respond in the format last, first, DOB."

    # Send reply within the same thread
    send_reply(gmail_service, "me", message, reply_message, pdf_path)

    # Store thread_id and history_id for later use (e.g., in a database or in-memory store)
    store_thread_info(thread_id, history_id)

    # Initiate watch on the specified label
    start_watch(gmail_service, label_name)
    
    # Since we're handling the reply asynchronously via the webhook, we don't wait here
    return  # Processing will continue in the webhook when the user's reply is received
    

    
 


