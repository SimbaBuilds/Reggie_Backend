from pydantic import BaseModel

class StatsResponse(BaseModel):
    count: int