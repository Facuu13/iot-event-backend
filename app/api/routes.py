import logging
from fastapi import APIRouter, BackgroundTasks
from app.models.event import SensorEvent
from app.core.rabbitmq import publish_event
from app.core.db import get_last_events
from typing import List

logger = logging.getLogger("api")

router = APIRouter()
events_db: List[SensorEvent] = []

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/ingest")
def ingest_event(event: SensorEvent, background_tasks: BackgroundTasks):
    events_db.append(event)
    payload = event.model_dump(mode="json")

    logger.info(f"ingest accepted event_id={event.event_id} device_id={event.device_id}")
    background_tasks.add_task(publish_event, payload)

    return {"message": "Event stored + enqueued", "event_id": event.event_id}

@router.get("/events")
def get_events():
    return events_db

@router.get("/events/db")
def get_events_db(limit: int = 50):
    return get_last_events(limit)