
# IoT Event-Driven Backend (FastAPI + RabbitMQ + SQLite)

An event-driven IoT ingestion backend built with FastAPI, RabbitMQ and SQLite.

This project simulates a real-world IoT architecture where devices send telemetry events to an API, which publishes them to a message broker. A worker service consumes those events, processes them and stores them persistently.

---

## 🏗️ Architecture

```

Device → FastAPI → RabbitMQ → Worker → SQLite

````

### Components

- **FastAPI API**
  - Validates incoming sensor events
  - Publishes events to RabbitMQ
  - Provides read endpoints

- **RabbitMQ**
  - Durable queues
  - Retry queue with TTL
  - Dead Letter Queue (DLQ)

- **Worker**
  - Consumes events
  - Stores them in SQLite
  - Handles retries
  - Sends failed messages to DLQ after max attempts

- **SQLite**
  - Persistent event storage

---

## 📦 Features

- Event validation with Pydantic
- UUID-based `event_id`
- Durable message publishing
- Retry mechanism with configurable delay
- Dead Letter Queue support
- Docker Compose orchestration
- Structured logging
- Device simulator (external tool)

---

## 🚀 Running the Project

### 1️⃣ Build and start services

```bash
docker compose up --build
````

This starts:

* API → [http://localhost:8000](http://localhost:8000)
* RabbitMQ → [http://localhost:15672](http://localhost:15672) (guest/guest)
* Worker (background consumer)

---

### 2️⃣ API Documentation

Interactive docs available at:

```
http://localhost:8000/docs
```

---

## 📡 Example Event

POST `/ingest`

```json
{
  "device_id": "esp32-01",
  "temperature": 24.5,
  "humidity": 60.2,
  "timestamp": "2026-02-27T15:00:00Z"
}
```

Response:

```json
{
  "message": "Event stored + enqueued",
  "event_id": "generated-uuid"
}
```

---

## 📊 Read Stored Events

Get latest events from SQLite:

```
GET /events/db
```

---

## 🔁 Retry & Dead Letter Mechanism

If processing fails:

1. Message is sent to `iot.events.retry`
2. It waits for configured TTL
3. It returns to main queue
4. After `MAX_RETRIES`, it goes to `iot.events.dlq`

Queues:

* `iot.events`
* `iot.events.retry`
* `iot.events.dlq`

You can inspect them via RabbitMQ management UI.

---

## 🛠 Environment Variables

| Variable       | Description            | Default         |
| -------------- | ---------------------- | --------------- |
| RABBITMQ_HOST  | RabbitMQ hostname      | rabbitmq        |
| RABBITMQ_QUEUE | Main queue name        | iot.events      |
| DB_PATH        | SQLite DB path         | /data/events.db |
| MAX_RETRIES    | Maximum retry attempts | 5               |
| RETRY_DELAY_MS | Retry delay in ms      | 10000           |

---

## 🧪 Device Simulator (Optional)

A standalone `simulator.py` tool is provided.

Run it outside Docker:

```bash
python simulator.py
```

It generates random device telemetry and sends it to the API.

---

## 🧠 Learning Goals

This project focuses on:

* Event-driven architecture
* Message queue patterns
* Retry strategies
* Dead Letter Queue handling
* Decoupled services
* Backend system design for IoT

---

## 📂 Project Structure

```
app/
  api/
  core/
  models/
worker_db.py
tools/simulator.py
docker-compose.yml
Dockerfile.api
Dockerfile.worker
```

---





