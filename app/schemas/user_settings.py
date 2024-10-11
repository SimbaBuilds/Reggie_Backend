from pydantic import BaseModel

class Settings(BaseModel):
    organization_name: str
    email_signature: str

class SettingsResponse(BaseModel):
    settings: Settings

class UpdateSettingsResponse(BaseModel):
    message: str