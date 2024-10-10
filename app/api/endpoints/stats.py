from fastapi import APIRouter, Depends
from app.models import User
from app.utils.authenticate import get_current_user

router = APIRouter()

@router.get("/students-count")
async def get_students_count(current_user: User = Depends(get_current_user)):
    # Implement get students count logic
    pass

@router.get("/staff-count")
async def get_staff_count(current_user: User = Depends(get_current_user)):
    # Implement get staff count logic
    pass

@router.get("/templates-count")
async def get_templates_count(current_user: User = Depends(get_current_user)):
    # Implement get templates count logic
    pass