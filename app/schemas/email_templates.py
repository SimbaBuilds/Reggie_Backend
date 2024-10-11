from pydantic import BaseModel
from typing import List

class EmailTemplate(BaseModel):
    id: int
    name: str
    subject: str
    body: str

class EmailTemplateResponse(BaseModel):
    templates: List[EmailTemplate]

class EmailTemplateCreateResponse(BaseModel):
    id: int
    message: str

class EmailTemplateUpdateResponse(BaseModel):
    message: str

class EmailTemplateDeleteResponse(BaseModel):
    message: str