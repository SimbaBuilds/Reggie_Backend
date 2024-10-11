from pydantic import BaseModel

class CoverPageGenerationResponse(BaseModel):
    file_url: str

class CoverPageOrderResponse(BaseModel):
    order_id: str
    status: str