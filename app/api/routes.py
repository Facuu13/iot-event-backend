from fastapi import APIRouter, BackgroundTasks
from app.models.event import SensorEvent
from app.core.rabbitmq import publish_event
from typing import List
from app.core.db import get_last_events


router = APIRouter()

events_db: List[SensorEvent] = []

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/ingest")
def ingest_event(event: SensorEvent, background_tasks: BackgroundTasks):
    # guardado local para test (temporal)
    events_db.append(event)

    # encolar en rabbit (mandamos dict serializable)
    payload = event.model_dump(mode="json")  # Pydantic v2 friendly
    background_tasks.add_task(publish_event, payload)

    return {"message": "Event stored + enqueued"}

@router.get("/events")
def get_events():
    return events_db

@router.get("/events/db")
def get_events_db(limit: int = 50):
    return get_last_events(limit)