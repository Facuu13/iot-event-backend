from fastapi import APIRouter
from app.models.event import SensorEvent

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/ingest")
def ingest_event(event: SensorEvent):
    print(f"Received event from {event.device_id}")
    return {"message": "Event received"}