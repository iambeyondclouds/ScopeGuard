
import sqlite3
import json
from pathlib import Path


# Keep the database in the main project directory
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "scopeguard.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():

    with get_connection() as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT,
                target TEXT,
                timestamp TEXT,
                status TEXT,
                process TEXT
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                incident_id TEXT PRIMARY KEY,
                task TEXT,
                action TEXT,
                target TEXT,
                timestamp TEXT,
                decision TEXT,
                reason TEXT,
                severity TEXT,
                status TEXT
            )
        """)


def save_event(event):

    process = json.dumps(event.get("process"))

    with get_connection() as connection:
        connection.execute("""
            INSERT INTO events
            (action, target, timestamp, status, process)
            VALUES (?, ?, ?, ?, ?)
        """, (
            event["action"],
            event["target"],
            event["timestamp"],
            event["status"],
            process
        ))


def save_incident(incident):

    with get_connection() as connection:
        connection.execute("""
            INSERT OR IGNORE INTO incidents
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            incident["incident_id"],
            incident["task"],
            incident["action"],
            incident["target"],
            incident["timestamp"],
            incident["decision"],
            incident["reason"],
            incident["severity"],
            incident["status"]
        ))


def get_events():

    with get_connection() as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            "SELECT * FROM events ORDER BY id DESC"
        ).fetchall()

    events = []

    for row in rows:
        event = dict(row)
        event["process"] = json.loads(event["process"])
        events.append(event)

    return events


def get_incidents():

    with get_connection() as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            "SELECT * FROM incidents ORDER BY rowid DESC"
        ).fetchall()

    return [dict(row) for row in rows]

