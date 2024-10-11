from pydantic import BaseModel

class PubsubMessage(BaseModel):
    message: dict
    subscription: str