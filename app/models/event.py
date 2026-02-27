from pydantic import BaseModel, Field
from datetime import datetime
from uuid import uuid4

class SensorEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    device_id: str
    temperature: float
    humidity: float
    timestamp: datetime