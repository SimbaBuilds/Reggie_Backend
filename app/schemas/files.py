from pydantic import BaseModel
from typing import Dict, List, Optional

class CSVUploadResponse(BaseModel):
    success: bool
    message: str
    mapped_headers: Dict[str, str]
    rows_processed: int

class FileInfo(BaseModel):
    id: str
    name: str
    size: int
    created_at: str
    updated_at: str
    file_type: str

class FileListResponse(BaseModel):
    success: bool
    message: str
    files: List[FileInfo]

class FileUploadResponse(BaseModel):
    success: bool
    message: str
    file_info: FileInfo

class FileDeleteResponse(BaseModel):
    success: bool
    message: str
    deleted_file_id: str