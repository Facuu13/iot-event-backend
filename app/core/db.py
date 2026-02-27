import sqlite3
from typing import List, Dict, Any

DB_PATH = "events.db"

def get_last_events(limit: int = 50) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT event_id, device_id, temperature, humidity, timestamp
        FROM events
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))

    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]