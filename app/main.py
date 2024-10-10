from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import auth, digitization, roster, email_templates, files, stats, cover_pages, assistant, settings
from app.core.config import settings
from app.services.gmail_service import process_cum_files, process_misc_records
from app.utils.authenticate import authenticate
from app.services.drive_service import build_drive_service
from app.services.gmail_service import build_gmail_service
from dev.dev_utils import update_pubsub
import os

app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

csv_path = settings.ROSTER_FILE_PATH
root_drive_folder_names = ["Student Records", "Transcripts"]

# def process_cum_files(creds, gmail_service, drive_service, email_label_name, root_drive_folder_name, csv_path):
#     label_name = email_label_name  
#     label_id = get_label_id(gmail_service, label_name)
#     page_token = None
#     while True:
#         # Fetch unread messages with pagination
#         response = fetch_unread_with_label(label_id, gmail_service, page_token)
#         messages = response.get('messages', [])

#         if not messages:
#             break  # Exit the loop if no more messages are found
        
#         func1(creds, gmail_service, drive_service, email_label_name, root_drive_folder_name, csv_path)
#         page_token = response.get('nextPageToken', None)
        
#         if not page_token:
#             break  
#     print("All cum files processed")



# def process_misc_records(creds, gmail_service, drive_service, email_label_name, root_drive_folder_name, csv_path):
#     label_name = email_label_name  
#     label_id = get_label_id(gmail_service, label_name)
#     page_token = None
#     while True:
#         # Fetch unread messages with pagination
#         response = fetch_unread_with_label(label_id, gmail_service, page_token)
#         messages = response.get('messages', [])

#         if not messages:
#             break  # Exit the loop if no more messages are found
        
#         func2(creds, gmail_service, drive_service, email_label_name, root_drive_folder_name, csv_path)
#         page_token = response.get('nextPageToken', None)
        
#         if not page_token:
#             break  
#     print("All misc records processed")


# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(digitization.router, prefix="/api/digitize", tags=["Digitization"])
app.include_router(roster.router, prefix="/api/roster", tags=["Roster Management"])
app.include_router(email_templates.router, prefix="/api/email-templates", tags=["Email Templates"])
app.include_router(files.router, prefix="/api/files", tags=["File Management"])
app.include_router(stats.router, prefix="/api/stats", tags=["Dashboard Statistics"])
app.include_router(cover_pages.router, prefix="/api/cover-pages", tags=["Cover Pages"])
app.include_router(assistant.router, prefix="/api/assistant", tags=["Reggie Assistant"])
app.include_router(settings.router, prefix="/api/settings", tags=["Settings"])

@app.post("/process-files")
async def process_files(background_tasks: BackgroundTasks):
    background_tasks.add_task(process_all_files)
    return {"status": "File processing started"}

async def process_all_files():
    creds = authenticate()
    gmail_service = build_gmail_service()
    drive_service = build_drive_service()
    csv_path = settings.ROSTER_FILE_PATH
    
    await process_cum_files(csv_path)
    await process_misc_records(csv_path)

@app.on_event("startup")
async def startup_event():
    # Initialize services, database connections, etc.
    pass

@app.on_event("shutdown")
async def shutdown_event():
    # Clean up resources, close connections, etc.
    pass

ngrok_url = os.getenv("NGROK_URL")
update_pubsub("digitize-all-records", "DigitizeRecords", ngrok_url)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=8000)