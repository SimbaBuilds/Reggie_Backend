from pydantic import BaseModel

# Pub/Sub message data format (optional)
class PubSubMessage(BaseModel):
    message: dict
    subscription: str
