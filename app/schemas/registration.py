from pydantic import BaseModel
from typing import Optional 
from enum import Enum
from datetime import datetime


class SubscriptionType(str, Enum):
    free = "free"
    digitize_only = "digitize_only"
    full = "full"

class OrganizationType(str, Enum):
    school = "school"
    district = "district"
    other = "other"

class OrganizationSize(str, Enum):
    small = "small"
    large = "large"

class ProcessingStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    uploaded = "uploaded"
    failed = "failed"

class JobStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"


class UserCreate(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    email_alias: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    email_alias: Optional[str] = None
    message: str


class OrganizationCreate(BaseModel):
    name: str
    type: str
    size: str
    created_by: int

class OrganizationResponse(BaseModel):
    id: int
    name: str
    type: str
    size: str
    subscription_type: SubscriptionType
    created_by: int
    message: str

class ExistingOrganizationResponse(BaseModel):
    id: int
    name: str
    message: str


class GoogleUserData(BaseModel):
    email: str
    first_name: str
    last_name: str
    google_id: str
