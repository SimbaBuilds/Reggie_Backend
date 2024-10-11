from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.models import User  # This should be your database model
from app.utils.authenticate import get_current_user
from app.schemas.auth import LoginResponse, SignupResponse, LogoutResponse, UserResponse, UserCreate

router = APIRouter()

#CLERK SERVICE

@router.post("/login", response_model=LoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Implement login logic
    pass

