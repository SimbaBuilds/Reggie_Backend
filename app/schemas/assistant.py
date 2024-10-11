from pydantic import BaseModel

class AssistantQueryResponse(BaseModel):
    response: str