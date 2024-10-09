from pydantic import BaseModel

class DigitizationResponse(BaseModel):
    message: str

class FileManagementResponse(BaseModel):
    message: str

class EmailAutomationResponse(BaseModel):
    message: str

class RosterManagementResponse(BaseModel):
    message: str