from fastapi import APIRouter, Depends
from app.utils.auth import get_current_user
from app.models import User       
from app.schemas.stats import StatsResponse

router = APIRouter()

@router.get("/students-count", response_model=StatsResponse)
async def get_students_count(current_user: User = Depends(get_current_user)):
    # Implement get students count logic
    pass

@router.get("/staff-count", response_model=StatsResponse)
async def get_staff_count(current_user: User = Depends(get_current_user)):
    # Implement get staff count logic
    pass

@router.get("/templates-count", response_model=StatsResponse)
async def get_templates_count(current_user: User = Depends(get_current_user)):
    # Implement get templates count logic
    pass