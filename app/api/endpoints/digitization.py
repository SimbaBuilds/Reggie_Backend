from fastapi import APIRouter, BackgroundTasks, UploadFile, File, Depends
from sqlalchemy.orm import Session
from app.services.gmail_service import process_cum_files, process_misc_records, process_transcript_batch
from app.schemas.base import DigitizationResponse
from app.db.session import get_db
from app.utils.authenticate import authenticate
from app.services.drive_service import build_drive_service
from app.services.gmail_service import build_gmail_service
from app.core.config import settings

router = APIRouter()

@router.post("/digitize-records", response_model=DigitizationResponse)
async def digitize_records(background_tasks: BackgroundTasks, file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_path = f"temp/{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    creds = authenticate()
    gmail_service = build_gmail_service()
    drive_service = build_drive_service()
    csv_path = settings.ROSTER_FILE_PATH

    background_tasks.add_task(process_cum_files, creds, gmail_service, drive_service, "Cumulative Files", "Student Records", csv_path)
    background_tasks.add_task(process_misc_records, creds, gmail_service, drive_service, "Miscellaneous Records", "Student Records", csv_path)
    
    return {"message": "Digitization process started"}

@router.post("/upload-transcript-batch", response_model=DigitizationResponse)
async def upload_transcript_batch(background_tasks: BackgroundTasks, file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_path = f"temp/{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    creds = authenticate()
    gmail_service = build_gmail_service()
    drive_service = build_drive_service()
    
    background_tasks.add_task(process_transcript_batch, creds, gmail_service, drive_service, file_path)
    
    return {"message": "Transcript batch upload started"}