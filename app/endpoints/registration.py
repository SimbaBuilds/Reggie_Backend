from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List
from supabase import create_client, Client
from app.utils.auth import verify_token, create_access_token
from app.core.config import settings
from app.models import Organization, OrganizationType, OrganizationSize, User
from app.utils.auth import pwd_context
from app.schemas.registration import UserCreate, OrganizationCreate, UserResponse, OrganizationResponse, SubscriptionType, GoogleUserData
from app.db.session import get_db


router = APIRouter()

# Supabase client initialization
supabase: Client = create_client(
    supabase_url=settings.SUPABASE_URL,
    supabase_key=settings.SUPABASE_KEY
)


@router.post("/signup/user", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup_user(user_data: UserCreate, supabase = Depends(get_db)):
    try:
        # Check if user already exists
        existing_user = supabase.table("user").select("*").eq("email", user_data.email).execute()
        if existing_user.data:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        # Check if organization exists
        # Hash the password
        hashed_password = pwd_context.hash(user_data.password)
        
        # Create new user
        new_user = {
            "email": user_data.email,
            "hashed_password": hashed_password,
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "email_alias": user_data.email_alias or None
        }
        
        result = supabase.table("user").insert(new_user).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create user")
        
        created_user = result.data[0]
        
        return UserResponse(
            id=created_user['id'],
            email=created_user['email'],
            first_name=created_user['first_name'],
            last_name=created_user['last_name'],
            email_alias=created_user['email_alias'],
            message="User created successfully"
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.post("/signup/organization", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def signup_organization(org_data: OrganizationCreate, supabase = Depends(get_db)):
    try:
        # Check if organization already exists
        existing_org = supabase.table("organization").select("*").eq("name", org_data.name).execute()
        if existing_org.data:
            raise HTTPException(status_code=400, detail="Organization with this name already exists")
        
        # Create new organization
        new_org = {
            "name": org_data.name,
            "type": org_data.type,
            "size": org_data.size,
            "subscription_type": SubscriptionType.free,  # Default subscription type
            "created_by": org_data.created_by
        }
        
        result = supabase.table("organization").insert(new_org).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create organization")
        
        created_org = result.data[0]
        
        # Update user with organization_id
        supabase.table("user").update({"organization_id": created_org['id']}).eq("id", org_data.created_by).execute()
        
        return OrganizationResponse(
            id=created_org['id'],
            name=created_org['name'],
            type=created_org['type'],
            size=created_org['size'],
            subscription_type=created_org['subscription_type'],
            created_by=created_org['created_by'],
            message="Organization created successfully"
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    

@router.get("/organizations", response_model=List[Organization])
async def get_organizations(
    name: str = "",
    user_payload: dict = Depends(verify_token)
):
    try:
        # Query organizations from Supabase
        query = supabase.table("organization").select("*")
        
        if name:
            query = query.ilike("name", f"%{name}%")
        
        data, error = query.execute()

        if error:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch organizations: {error.message}")

        return [Organization(**org) for org in data[1]]

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")

class JoinOrganizationRequest(BaseModel):
    organization_id: int

@router.post("/join-organization", response_model=User)
async def join_organization(
    join_request: JoinOrganizationRequest,
    user_payload: dict = Depends(verify_token)
):
    try:
        user_id = user_payload.get("user_id")
        
        # Check if the organization exists
        org_data, org_error = supabase.table("organization").select("id, name").eq("id", join_request.organization_id).execute()
        if org_error or not org_data[1]:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

        org = org_data[1][0]

        # Check if user already belongs to an organization
        user_data, user_error = supabase.table("users").select("organization_id").eq("id", user_id).execute()
        if user_error:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch user data")
        
        if user_data[1] and user_data[1][0].get("organization_id"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already belongs to an organization")

        # Update user's organization in Supabase
        data, error = supabase.table("users").update({
            "organization_id": org["id"],
            "organization_name": org["name"]
        }).eq("id", user_id).execute()

        if error:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to join organization: {error.message}")

        return User(**data[1][0])

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")



@router.post("/signup/google", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup_google_user(user_data: GoogleUserData, supabase = Depends(get_db)):
    try:
        # Check if user already exists
        existing_user = supabase.table("user").select("*").eq("email", user_data.email).execute()
        if existing_user.data:
            # If user exists, return the existing user data with a different status code
            user = existing_user.data[0]
            return UserResponse(
                id=user['id'],
                email=user['email'],
                first_name=user['first_name'],
                last_name=user['last_name'],
                email_alias=user.get('email_alias'),
                message="User already exists",
                access_token=create_access_token(data={"sub": user['email']})
            ), status.HTTP_200_OK
        
        # Create new user
        new_user = {
            "email": user_data.email,
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "google_id": user_data.google_id,
            "auth_provider": "google"
        }
        
        result = supabase.table("user").insert(new_user).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create user")
        
        created_user = result.data[0]
        
        # Create access token
        access_token = create_access_token(data={"sub": created_user['email']})
        
        return UserResponse(
            id=created_user['id'],
            email=created_user['email'],
            first_name=created_user['first_name'],
            last_name=created_user['last_name'],
            email_alias=created_user.get('email_alias'),
            message="User created successfully",
            access_token=access_token
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
