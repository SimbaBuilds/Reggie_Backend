from fastapi import APIRouter, Depends
from app.utils.google_auth import get_current_user
from app.models import User 
from app.schemas.email_templates import EmailTemplateResponse, EmailTemplateCreateResponse, EmailTemplateUpdateResponse, EmailTemplateDeleteResponse

router = APIRouter()

@router.get("/", response_model=EmailTemplateResponse)
async def get_email_templates(current_user: User = Depends(get_current_user)):
    # Implement get email templates logic
    pass

@router.post("/", response_model=EmailTemplateCreateResponse)
async def create_email_template(current_user: User = Depends(get_current_user)):
    # Implement create email template logic
    pass

@router.put("/{template_id}", response_model=EmailTemplateUpdateResponse)
async def update_email_template(template_id: int, current_user: User = Depends(get_current_user)):
    # Implement update email template logic
    pass

@router.delete("/{template_id}", response_model=EmailTemplateDeleteResponse)
async def delete_email_template(template_id: int, current_user: User = Depends(get_current_user)):
    # Implement delete email template logic
    pass