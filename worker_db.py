import json
import sqlite3
import pika

RABBITMQ_HOST = "localhost"
QUEUE_NAME = "iot.events"
DB_PATH = "events.db"

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

    # para saber si insertó o ignoró (por duplicado)
    inserted = cur.rowcount == 1
    conn.close()
    return inserted

def main():
    init_db()

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    def callback(ch, method, properties, body):
        event = json.loads(body.decode("utf-8"))

        inserted = insert_event(event)
        if inserted:
            print("💾 Stored in SQLite:", event["event_id"])
        else:
            print("♻️ Duplicate ignored:", event["event_id"])

        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    print("👷 DB Worker running. Waiting for messages...")
    channel.start_consuming()

if __name__ == "__main__":
    main()