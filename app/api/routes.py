from fastapi import APIRouter
from app.models.event import SensorEvent
from typing import List

router = APIRouter()

# Simulación de base de datos en memoria
events_db: List[SensorEvent] = []

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/ingest")
def ingest_event(event: SensorEvent):
    events_db.append(event)
    return {"message": "Event stored"}

@router.get("/events")
def get_events():
    return events_db