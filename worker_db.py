import json
import sqlite3
import time
import pika

RABBITMQ_HOST = "localhost"

MAIN_QUEUE = "iot.events"
RETRY_QUEUE = "iot.events.retry"
DLQ_QUEUE = "iot.events.dlq"

DB_PATH = "events.db"

MAX_RETRIES = 5
RETRY_DELAY_MS = 10_000  # 10s


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            event_id TEXT PRIMARY KEY,
            device_id TEXT NOT NULL,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def insert_event(event: dict):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT OR IGNORE INTO events (event_id, device_id, temperature, humidity, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (
        event["event_id"],
        event["device_id"],
        event["temperature"],
        event["humidity"],
        event["timestamp"],
    ))
    conn.commit()
    inserted = cur.rowcount == 1
    conn.close()
    return inserted


def declare_queues(channel: pika.adapters.blocking_connection.BlockingChannel):
    # Main queue
    channel.queue_declare(queue=MAIN_QUEUE, durable=True)

    # Retry queue: mensajes duermen RETRY_DELAY_MS y vuelven a MAIN_QUEUE
    channel.queue_declare(
        queue=RETRY_QUEUE,
        durable=True,
        arguments={
            "x-message-ttl": RETRY_DELAY_MS,
            "x-dead-letter-exchange": "",
            "x-dead-letter-routing-key": MAIN_QUEUE,
        }
    )

    # Dead Letter Queue
    channel.queue_declare(queue=DLQ_QUEUE, durable=True)


def get_retry_count(properties: pika.BasicProperties) -> int:
    headers = properties.headers or {}
    return int(headers.get("x-retry-count", 0))


def publish_with_retry(channel, body_bytes: bytes, retry_count: int):
    props = pika.BasicProperties(
        delivery_mode=2,
        headers={"x-retry-count": retry_count},
        content_type="application/json",
    )
    channel.basic_publish(
        exchange="",
        routing_key=RETRY_QUEUE,
        body=body_bytes,
        properties=props,
    )


def publish_to_dlq(channel, body_bytes: bytes, retry_count: int, error_msg: str):
    props = pika.BasicProperties(
        delivery_mode=2,
        headers={
            "x-retry-count": retry_count,
            "x-last-error": error_msg[:200],  # acotamos
        },
        content_type="application/json",
    )
    channel.basic_publish(
        exchange="",
        routing_key=DLQ_QUEUE,
        body=body_bytes,
        properties=props,
    )


def main():
    init_db()

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    declare_queues(channel)

    def callback(ch, method, properties, body):
        retry_count = get_retry_count(properties)
        body_bytes = body  # para re-publicar igual

        try:
            event = json.loads(body.decode("utf-8"))

            # ✅ Procesamiento real
            inserted = insert_event(event)
            if inserted:
                print(f"💾 Stored: {event['event_id']}")
            else:
                print(f"♻️ Duplicate ignored: {event['event_id']}")

            # ✅ ACK
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            error_msg = f"{type(e).__name__}: {e}"
            print(f"❌ Failed (retry={retry_count}) → {error_msg}")

            # ⛔ Si ya llegamos al máximo → DLQ
            if retry_count >= MAX_RETRIES:
                publish_to_dlq(ch, body_bytes, retry_count, error_msg)
                print("🪦 Sent to DLQ")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            # 🔁 Reintento: mandamos a retry queue con retry_count+1
            publish_with_retry(ch, body_bytes, retry_count + 1)
            print(f"⏳ Sent to RETRY queue (next retry={retry_count + 1})")
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=MAIN_QUEUE, on_message_callback=callback)

    print("👷 DB Worker (with retries+DLQ) running...")
    channel.start_consuming()


if __name__ == "__main__":
    main()