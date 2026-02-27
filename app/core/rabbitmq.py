import json
import pika
from typing import Any, Dict

RABBITMQ_HOST = "localhost"
QUEUE_NAME = "iot.events"

def publish_event(payload: Dict[str, Any]) -> None:
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    channel = connection.channel()

    # durable=True para que la cola sobreviva reinicios del broker
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    channel.basic_publish(
        exchange="",
        routing_key=QUEUE_NAME,
        body=json.dumps(payload).encode("utf-8"),
        properties=pika.BasicProperties(
            delivery_mode=2  # mensaje persistente
        ),
    )

    connection.close()