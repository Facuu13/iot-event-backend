from pydantic import BaseModel
from datetime import datetime

class SensorEvent(BaseModel):
    device_id: str
    temperature: float
    humidity: float
    timestamp: datetime