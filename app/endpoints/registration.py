from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List
from supabase import create_client, Client
from app.utils.auth import verify_token, create_access_token
from app.core.config import settings
from app.models import Organization, OrganizationType, OrganizationSize, User
from app.utils.auth import pwd_context
from app.schemas.registration import UserCreate, OrganizationCreate, UserResponse, OrganizationResponse, SubscriptionType, GoogleUserData, ExistingOrganizationResponse
from app.db.session import get_db
import secrets
import logging
from fastapi import Query
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Supabase client initialization
supabase: Client = create_client(
    supabase_url=settings.SUPABASE_URL,
    supabase_key=settings.SUPABASE_KEY
)

#region User Signup

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
        
        # Generate a random string for hashed_password
        placeholder_password = secrets.token_hex(16)
        hashed_placeholder = pwd_context.hash(placeholder_password)
        
        # Create new user
        new_user = {
            "email": user_data.email,
            "hashed_password": hashed_placeholder,  # Use placeholder for Google users
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "email_alias": None,  # Assuming Google users don't have an email alias
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

#endregion

#region Organization Details

@router.post("/create/organization", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(org_data: OrganizationCreate, supabase = Depends(get_db)):
    try:
        logger.info(f"Received organization data: {org_data.dict()}")
        
        # Check if organization already exists
        existing_org = supabase.table("organization").select("*").eq("name", org_data.name).execute()
        logger.info(f"Existing organization query result: {existing_org}")
        
        if existing_org.data:
            logger.warning(f"Organization with name '{org_data.name}' already exists")
            raise HTTPException(status_code=400, detail="Organization with this name already exists")
        
        # Create new organization
        new_org = {
            "name": org_data.name,
            "type": org_data.type,
            "size": org_data.size,
            "subscription_type": SubscriptionType.free.value,  # Default subscription type
            "created_by": org_data.created_by
        }
        logger.info(f"New organization data: {new_org}")
        
        result = supabase.table("organization").insert(new_org).execute()
        logger.info(f"Insert result: {result}")
        
        if not result.data:
            logger.error("Failed to create organization: No data returned")
            raise HTTPException(status_code=500, detail="Failed to create organization")
        
        created_org = result.data[0]
        logger.info(f"Created organization: {created_org}")
        
        # Update user with organization_id
        user_update_result = supabase.table("user").update({"organization_id": created_org['id']}).eq("id", org_data.created_by).execute()
        logger.info(f"User update result: {user_update_result}")
        
        return OrganizationResponse(
            id=created_org['id'],
            name=created_org['name'],
            type=created_org['type'],
            size=created_org['size'],
            subscription_type=SubscriptionType(created_org['subscription_type']),
            created_by=created_org['created_by'],
            message="Organization created successfully"
        )
    except HTTPException as http_exc:
        logger.error(f"HTTP Exception: {http_exc}")
        raise http_exc
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    

@router.get("/get-organization", response_model=ExistingOrganizationResponse)
async def get_organization(
    name: str = Query("", description="Name of the organization to check"),
    id: int = Query(None, description="ID of the organization to check")
):
    query = supabase.table("organization").select("*")
    
    if name:
        query = query.ilike("name", f"%{name}%")
    if id is not None:
        query = query.eq("id", id)
    
    result = query.execute()

    if result.error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"Failed to fetch organizations: {result.error.message}")

    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="No organizations found matching the criteria")

    return ExistingOrganizationResponse(
        id=result.data[0]['id'],
        name=result.data[0]['name'],
        message="Organization found successfully"
    )

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

#endregion



