from googleapiclient.discovery import build
try:
    from utils.process_cum_files import get_label_id
    from utils.process_cum_files import process_hundred_messages as func1
    from app.utils.handle_misc_records import process_hundred_messages as func2
    from utils.authenticate import authenticate
    from utils.gmail_utils import fetch_unread_with_label
    from endpoints import gmail_webhook
    from dev.dev_utils import update_pubsub
    from utils.handle_misc_records import email_label_names
except ModuleNotFoundError:
    from app.utils.process_cum_files import get_label_id
    from app.utils.process_cum_files import process_hundred_messages as func1
    from app.utils.handle_misc_records import process_hundred_messages as func2
    from app.utils.authenticate import authenticate
    from app.utils.gmail_utils import fetch_unread_with_label
    from app.endpoints import gmail_webhook
    from app.utils.handle_misc_records import email_label_names
from fastapi import FastAPI, BackgroundTasks
from app.utils.gmail_utils import build_gmail_service, start_watch_for_labels
import uvicorn
import os
from google.cloud import pubsub_v1






app = FastAPI()


#include endpoints via router

app.include_router(gmail_webhook.router)


from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Specify domains if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

csv_path = 'ESD.csv'
root_drive_folder_names = ["Student Records", "Transcripts"]

def process_cum_files(creds, gmail_service, drive_service, email_label_name, root_drive_folder_name, csv_path):
    label_name = email_label_name  
    label_id = get_label_id(gmail_service, label_name)
    page_token = None
    while True:
        # Fetch unread messages with pagination
        response = fetch_unread_with_label(label_id, gmail_service, page_token)
        messages = response.get('messages', [])

        if not messages:
            break  # Exit the loop if no more messages are found
        
        func1(creds, gmail_service, drive_service, email_label_name, root_drive_folder_name, csv_path)
        page_token = response.get('nextPageToken', None)
        
        if not page_token:
            break  
    print("All cum files processed")



def process_misc_records(creds, gmail_service, drive_service, email_label_name, root_drive_folder_name, csv_path):
    label_name = email_label_name  
    label_id = get_label_id(gmail_service, label_name)
    page_token = None
    while True:
        # Fetch unread messages with pagination
        response = fetch_unread_with_label(label_id, gmail_service, page_token)
        messages = response.get('messages', [])

        if not messages:
            break  # Exit the loop if no more messages are found
        
        func2(creds, gmail_service, drive_service, email_label_name, root_drive_folder_name, csv_path)
        page_token = response.get('nextPageToken', None)
        
        if not page_token:
            break  
    print("All misc records processed")



# You can add API endpoints to trigger these processing functions if needed.
@app.post("/process-files")
async def process_files(background_tasks: BackgroundTasks):
    background_tasks.add_task(process_all_files)
    return {"status": "File processing started"}

async def process_all_files():
    creds = authenticate()
    gmail_service = build('gmail', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)

    for i in range(0, len(email_label_names)):
        process_cum_files(creds, gmail_service, drive_service, email_label_names[1], root_drive_folder_names[0], csv_path)
        process_misc_records(creds, gmail_service, drive_service, email_label_names[0], root_drive_folder_names[0], csv_path)

@app.on_event("startup")
async def startup_event():
    service = build_gmail_service()
    start_watch_for_labels(service, email_label_names)

ngrok_url = "https://moderately-thankful-bird.ngrok-free.app/"
gcloud_webhook_url = ""

if __name__ == '__main__':
    
    update_pubsub("digitize-all-records", "DigitizeRecords", ngrok_url) #pass ngrok url or gcloud webhook url
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)




#uvicorn app:app --reload --host 0.0.0.0 --port 8000
#ngrok http 8000

# Directory Structure
# REGGIE/
# │
# ├── __pycache__/
# │
# ├── app/
# │   ├── __pycache__/
# │   ├── endpoints/
# │   └── utils/
# │       ├── __init__.py
# │       ├── main.py
# │       └── schemas.py
# │
# ├── node_modules/
# ├── venv/
# ├── .gitignore
# ├── credentials.json
# ├── dev_utils.py
# └── Dockerfile