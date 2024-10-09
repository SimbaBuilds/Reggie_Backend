from fastapi import APIRouter, BackgroundTasks
from app.services.gmail_service import setup_email_automations
from app.schemas.base import EmailAutomationResponse

router = APIRouter()

@router.post("/setup-email-automations", response_model=EmailAutomationResponse)
async def setup_automations(background_tasks: BackgroundTasks):
    background_tasks.add_task(setup_email_automations)
    return {"message": "Email automation setup process started"}