import os
import time
import random
import requests
from datetime import datetime, timezone

API_URL = os.getenv("API_URL", "http://localhost:8000/ingest")
DEVICE_COUNT = int(os.getenv("DEVICE_COUNT", "3"))
INTERVAL_SEC = float(os.getenv("INTERVAL_SEC", "2.0"))

def make_event(device_id: str) -> dict:
    return {
        "device_id": device_id,
        "temperature": round(random.uniform(18.0, 35.0), 2),
        "humidity": round(random.uniform(30.0, 85.0), 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

def main():
    devices = [f"esp32-{i+1:02d}" for i in range(DEVICE_COUNT)]
    print(f"📡 Simulator starting: devices={devices} interval={INTERVAL_SEC}s api={API_URL}")

    while True:
        for d in devices:
            payload = make_event(d)
            try:
                r = requests.post(API_URL, json=payload, timeout=3)
                print(f"➡️  sent {d} status={r.status_code} event_id={r.json().get('event_id')}")
            except Exception as e:
                print(f"❌ send failed for {d}: {e}")
        time.sleep(INTERVAL_SEC)

if __name__ == "__main__":
    main()