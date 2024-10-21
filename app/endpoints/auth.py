from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from app.db.session import get_db
from app.schemas.auth import LoginResponse, SignupResponse, LogoutResponse, UserResponse, UserCreate, Token
from app.core.config import settings

router = APIRouter()

# This should be a more secure key stored in environment variables
SECRET_KEY = settings.JWT_SECRET    
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Helper functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), supabase = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
    user = supabase.table("user").select("*").eq("email", email).execute()
    if not user.data:
        raise HTTPException(status_code=404, detail="User not found")
    return user.data[0]

@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate, supabase = Depends(get_db)):
    try:
        # Check if user already exists
        existing_user = supabase.table("user").select("*").eq("email", user_data.email).execute()
        if existing_user.data:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        # Hash the password
        hashed_password = pwd_context.hash(user_data.password)
        
        # Create new user
        new_user = {
            "email": user_data.email,
            "hashed_password": hashed_password,
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

@router.post("/login", response_model=LoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), supabase = Depends(get_db)):
    user = supabase.table("user").select("*").eq("email", form_data.username).execute()
    if not user.data or not pwd_context.verify(form_data.password, user.data[0]['hashed_password']):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.data[0]['email']}, expires_delta=access_token_expires
    )
    return LoginResponse(access_token=access_token, token_type="bearer")

@router.post("/logout", response_model=LogoutResponse)
async def logout(response: Response, current_user: dict = Depends(get_current_user)):
    response.delete_cookie(key="access_token")
    return LogoutResponse(message="Logged out successfully")

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(**current_user)

@router.get("/token", response_model=Token)
async def get_token(current_user: dict = Depends(get_current_user)):
    access_token = create_access_token(data={"sub": current_user["email"]})
    return Token(access_token=access_token, token_type="bearer")
