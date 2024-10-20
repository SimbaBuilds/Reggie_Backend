from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List
from supabase import create_client, Client
from app.utils.authenticate import verify_token
from app.core.config import settings
from app.models import Organization, OrganizationType, OrganizationSize, User

router = APIRouter()

# Supabase client initialization
supabase: Client = create_client(
    supabase_url=settings.SUPABASE_URL,
    supabase_key=settings.SUPABASE_KEY
)

class OrganizationCreate(BaseModel):
    name: str
    type: OrganizationType
    size: OrganizationSize

@router.post("/api/organization", response_model=Organization)
async def create_organization(
    org_details: OrganizationCreate,
    user_payload: dict = Depends(verify_token)
):
    try:
        user_id = user_payload.get("user_id")
        
        # Check if user already has an organization
        user_data, user_error = supabase.table("users").select("organization_id, organization_name").eq("id", user_id).execute()
        if user_error:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch user data")
        
        if user_data[1] and user_data[1][0].get("organization_id"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already belongs to an organization")

        # Insert organization details into Supabase
        org_data, org_error = supabase.table("organization").insert({
            "name": org_details.name,
            "type": org_details.type,
            "size": org_details.size,
            "created_by": user_id
        }).execute()

        if org_error:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create organization: {org_error.message}")

        new_org = org_data[1][0]
        new_org_id = new_org["id"]
        new_org_name = new_org["name"]

        # Update user's organization_id and organization_name
        _, update_error = supabase.table("users").update({
            "organization_id": new_org_id,
            "organization_name": new_org_name
        }).eq("id", user_id).execute()
        
        if update_error:
            # Rollback organization creation if user update fails
            supabase.table("organization").delete().eq("id", new_org_id).execute()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update user's organization")

        return Organization(**new_org)

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")

@router.get("/api/organizations", response_model=List[Organization])
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

@router.post("/api/join-organization", response_model=User)
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
