from fastapi import APIRouter, BackgroundTasks
from app.utils.authenticate import get_current_user
from app.models import User
from app.schemas.email_automation import EmailAutomationResponse

router = APIRouter()

@router.post("/setup-email-automations", response_model=EmailAutomationResponse)
async def setup_automations(background_tasks: BackgroundTasks):
    return {"message": "Email automation setup process started"}