from fastapi import APIRouter, BackgroundTasks, UploadFile, File
from app.services.roster_service import update_roster
from app.schemas.base import RosterManagementResponse

router = APIRouter()

@router.post("/update-roster", response_model=RosterManagementResponse)
async def update_roster_endpoint(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    file_path = f"temp/{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    background_tasks.add_task(update_roster, file_path)
    
    return {"message": "Roster update process started"}