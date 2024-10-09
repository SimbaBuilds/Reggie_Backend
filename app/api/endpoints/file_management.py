from fastapi import APIRouter, BackgroundTasks
from app.services.drive_service import organize_and_upload_files
from app.schemas.base import FileManagementResponse

router = APIRouter()

@router.post("/organize-and-upload", response_model=FileManagementResponse)
async def organize_and_upload(background_tasks: BackgroundTasks):
    background_tasks.add_task(organize_and_upload_files)
    return {"message": "File organization and upload process started"}