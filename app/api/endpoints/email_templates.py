from fastapi import APIRouter, Depends
from app.models import User
from app.utils.authenticate import get_current_user

router = APIRouter()

@router.get("/")
async def get_email_templates(current_user: User = Depends(get_current_user)):
    # Implement get email templates logic
    pass

@router.post("/")
async def create_email_template(current_user: User = Depends(get_current_user)):
    # Implement create email template logic
    pass

@router.put("/{template_id}")
async def update_email_template(template_id: int, current_user: User = Depends(get_current_user)):
    # Implement update email template logic
    pass

@router.delete("/{template_id}")
async def delete_email_template(template_id: int, current_user: User = Depends(get_current_user)):
    # Implement delete email template logic
    pass