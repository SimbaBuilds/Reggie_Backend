from pydantic import BaseModel
from typing import Dict, Optional

class DigitizationResponse(BaseModel):
    message: str

class DigitizationStatus(BaseModel):
    status: str
    progress: float
    details: Optional[str] = None



class DigitizationStartRequest(BaseModel):
    file_type: str
    additional_params: Optional[Dict[str, str]] = None

class TranscriptBatchUploadResponse(BaseModel):
    message: str
    batch_id: str
    files_processed: int
