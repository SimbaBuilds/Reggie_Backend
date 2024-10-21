from fastapi import APIRouter, BackgroundTasks, UploadFile, File
from app.utils.google_auth import get_current_user
from app.models import User 
from app.schemas.roster_management import RosterManagementResponse

router = APIRouter()

@router.post("/update-roster", response_model=RosterManagementResponse)
async def update_roster_endpoint(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    file_path = f"temp/{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    
   
    return {"message": "Roster update process started"}