from fastapi import APIRouter, BackgroundTasks, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.files import CSVUploadResponse
from app.schemas.digitization import DigitizationResponse, DigitizationStatus, DigitizationStartRequest, TranscriptBatchUploadResponse
from app.db.session import get_db
from app.utils.authenticate import authenticate
from app.services.drive_service import build_drive_service
from app.services.gmail_service import build_gmail_service
from app.core.config import settings
from app.models import User
from app.services.ai_service import map_csv_headers
from app.utils.csv_processor import process_csv
from app.utils.validate_csv import validate_csv
from app.utils.authenticate import get_current_user
from app.utils.process_cum_files import process_cum_files
from app.utils.handle_misc_records import process_misc_records
from app.utils.process_transcript_batch import process_transcript_batch
import pandas as pd
import io

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

@router.post("/start")
async def start_digitization(current_user: User = Depends(get_current_user)):
    # Implement digitization start logic
    pass

@router.get("/status")
async def get_digitization_status(current_user: User = Depends(get_current_user)):
    # Implement digitization status check
    pass

@router.post("/upload/student-csv", response_model=CSVUploadResponse)
async def upload_student_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    supabase = Depends(get_db)
):
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Validate CSV
        required_columns = ["first_name", "last_name", "date_of_birth", "grade"]
        validation_result = validate_csv(df, required_columns, "student")
        if not validation_result["is_valid"]:
            return CSVUploadResponse(
                success=False,
                message=f"CSV validation failed: {validation_result['error']}",
                mapped_headers={},
                rows_processed=0
            )
        
        # Use AI model to map headers
        mapped_headers = map_csv_headers(df.columns.tolist(), "student")
        
        # Process the CSV with mapped headers
        processed_df = process_csv(df, mapped_headers, "student")
        
        # Get the organization for the current user
        organization = supabase.table("organization").select("*").eq("name", current_user.organization_name).execute()
        if not organization.data:
            raise HTTPException(status_code=404, detail="Organization not found")
        org_id = organization.data[0]['id']
        
        # Prepare student data for insertion
        students_data = []
        for _, row in processed_df.iterrows():
            student = {
                "organization_id": org_id,
                "first_name": row['first_name'],
                "last_name": row['last_name'],
                "date_of_birth": row['date_of_birth'],
                "grade": row['grade']
            }
            students_data.append(student)
        
        # Insert students into the database
        result = supabase.table("student").insert(students_data).execute()
        
        return CSVUploadResponse(
            success=True,
            message="Student CSV uploaded and processed successfully",
            mapped_headers=mapped_headers,
            rows_processed=len(processed_df)
        )
    except Exception as e:
        return CSVUploadResponse(
            success=False,
            message=f"Error processing CSV: {str(e)}",
            mapped_headers={},
            rows_processed=0
        )

@router.post("/upload/staff-csv", response_model=CSVUploadResponse)
async def upload_staff_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    supabase = Depends(get_db)
):
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Validate CSV
        required_columns = ["first_name", "last_name", "date_of_birth"]
        validation_result = validate_csv(df, required_columns, "staff")
        if not validation_result["is_valid"]:
            return CSVUploadResponse(
                success=False,
                message=f"CSV validation failed: {validation_result['error']}",
                mapped_headers={},
                rows_processed=0
            )
        
        # Use AI model to map headers
        mapped_headers = map_csv_headers(df.columns.tolist(), "staff")
        
        # Process the CSV with mapped headers
        processed_df = process_csv(df, mapped_headers, "staff")
        
        # Get the organization for the current user
        organization = supabase.table("organization").select("*").eq("name", current_user.organization_name).execute()
        if not organization.data:
            raise HTTPException(status_code=404, detail="Organization not found")
        org_id = organization.data[0]['id']
        
        # Prepare staff data for insertion
        staff_data = []
        for _, row in processed_df.iterrows():
            staff = {
                "organization_id": org_id,
                "first_name": row['first_name'],
                "last_name": row['last_name'],
                "date_of_birth": row['date_of_birth']
            }
            staff_data.append(staff)
        
        # Insert staff into the database
        result = supabase.table("staff").insert(staff_data).execute()
        
        return CSVUploadResponse(
            success=True,
            message="Staff CSV uploaded and processed successfully",
            mapped_headers=mapped_headers,
            rows_processed=len(processed_df)
        )
    except Exception as e:
        return CSVUploadResponse(
            success=False,
            message=f"Error processing CSV: {str(e)}",
            mapped_headers={},
            rows_processed=0
        )