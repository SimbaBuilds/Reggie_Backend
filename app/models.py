from pydantic import BaseModel, Field, Json
from datetime import datetime, date
from typing import Optional, List
from enum import Enum
from typing import Literal


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

#table name is "user"
class User(BaseModel):
    id: Optional[int] = None
    email: str
    hashed_password: Optional[str] = None
    first_name: str
    last_name: str
    organization_id: int
    organization_name: str
    created_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    email_alias: Optional[str] = None

#table name is "organization"
class Organization(BaseModel):
    id: int
    name: str
    created_at: datetime = Field(default_factory=datetime.now)
    type: OrganizationType
    size: OrganizationSize
    created_by: int
    rosters_uploaded: bool = False
    records_digitized: bool = False
    records_organized: bool = False
    transcripts_uploaded: bool = False
    email_labels_created: bool = False
    email_template_created: bool = False
    subscription_type: SubscriptionType

#table name is "student"
class Student(BaseModel):
    id: Optional[int] = None
    organization_id: int
    first_name: str
    last_name: str
    date_of_birth: date
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

#table name is "staff"
class Staff(BaseModel):
    id: Optional[int] = None
    organization_id: int
    first_name: str
    last_name: str
    date_of_birth: date
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

#table name is "record_processing"
class RecordProcessing(BaseModel):
    id: Optional[int] = None
    student_id: Optional[int] = None
    staff_id: Optional[int] = None
    original_filename: str
    status: ProcessingStatus
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None
    cloud_upload_path: Optional[str] = None

#table name is "digitization_job"
class DigitizationJob(BaseModel):
    id: Optional[int] = None
    user_id: int
    status: JobStatus
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

#table name is "email_automation"
class EmailAutomation(BaseModel):
    id: Optional[int] = None
    user_id: int
    label: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    last_triggered: Optional[datetime] = None
    total_emails_processed: int = 0

#table name is "email_template"
class EmailTemplate(BaseModel):
    id: Optional[int] = None
    user_id: int
    name: str
    description: Optional[str] = None
    content: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

#table name is "audit_log"
class AuditLog(BaseModel):
    id: Optional[int] = None
    user_id: int
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    details: Optional[Json] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

#table name is "user_usage"
class UserUsage(BaseModel):
    id: Optional[int] = None
    user_id: int
    date: date
    emails_sent_to_reggie: int = 0
    cumulative_files_processed: int = 0
    miscellaneous_labeled_processed: int = 0
    miscellaneous_unlabeled_processed: int = 0
    records_requests_processed: int = 0
    template_responses_processed: int = 0

#table name is "email_thread_info"
class EmailThreadInfo(BaseModel):
    thread_id: str
    history_id: Optional[str] = None


