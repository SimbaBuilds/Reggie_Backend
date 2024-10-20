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

@router.post("/signup", response_model=SignupResponse)
async def signup(user_data: UserCreate, supabase = Depends(get_db)):
    try:
        # Check if user already exists
        existing_user = supabase.table("user").select("*").eq("email", user_data.email).execute()
        if existing_user.data:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        # Create new user
        new_user = {
            "email": user_data.email,
            "hashed_password": user_data.password,  # Note: In production, hash the password before storing
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "organization_name": user_data.organization_name,
            "is_gsuite_user": user_data.is_gsuite_user,
            "subscription_type": "free"  # Default subscription type
        }
        
        result = supabase.table("user").insert(new_user).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create user")
        
        created_user = result.data[0]
        
        return SignupResponse(
            id=created_user['id'],
            email=created_user['email'],
            first_name=created_user['first_name'],
            last_name=created_user['last_name'],
            organization_name=created_user['organization_name'],
            is_gsuite_user=created_user['is_gsuite_user'],
            subscription_type=created_user['subscription_type'],
            message="User created successfully"
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
