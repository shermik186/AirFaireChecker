import json
import sqlite3
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "flights.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            departure TEXT,
            arrival TEXT,
            departure_time TEXT,
            arrival_time TEXT,
            price INTEGER,
            duration INTEGER,
            stops INTEGER,
            bags TEXT,
            nmb_of_adults TEXT,
            segments TEXT,
            layovers TEXT,
            checked_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def insert_flights(flights):
    conn = get_connection()
    cursor = conn.cursor()

    for flight in flights:
        cursor.execute("""
            INSERT INTO flights (
                departure,
                arrival,
                departure_time,
                arrival_time,
                price,
                duration,
                stops,
                bags,
                nmb_of_adults,
                segments,
                layovers,
                checked_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            flight.get("from"),
            flight.get("to"),
            flight.get("departure_time"),
            flight.get("arrival_time"),
            flight.get("price"),
            flight.get("duration"),
            flight.get("stops"),
            json.dumps(flight.get("bags"), ensure_ascii=False),
            flight.get("nmb_of_adults"),
            json.dumps(flight.get("segments"), ensure_ascii=False),
            json.dumps(flight.get("layovers"), ensure_ascii=False),
            flight.get("checked_at"),
        ))

    conn.commit()
    conn.close()


def get_flights_by_route(departure, arrival):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            departure,
            arrival,
            departure_time,
            arrival_time,
            price,
            duration,
            stops,
            bags,
            nmb_of_adults,
            segments,
            layovers,
            checked_at
        FROM flights
        WHERE departure = ? AND arrival = ?
        ORDER BY checked_at ASC
    """, (departure, arrival))

    rows = cursor.fetchall()
    conn.close()

    flights = []

    for row in rows:
        flights.append({
            "from": row[0],
            "to": row[1],
            "departure_time": row[2],
            "arrival_time": row[3],
            "price": row[4],
            "duration": row[5],
            "stops": row[6],
            "bags": json.loads(row[7]) if row[7] else None,
            "nmb_of_adults": row[8],
            "segments": json.loads(row[9]) if row[9] else [],
            "layovers": json.loads(row[10]) if row[10] else [],
            "checked_at": row[11],
        })

    return flights


def clean_old_flights():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            departure_time
        FROM flights
    """)

    rows = cursor.fetchall()
    today = datetime.today().date()

    old_ids = []

    for row in rows:
        flight_id = row[0]
        departure_time = row[1]

        try:
            flight_date = datetime.strptime(departure_time, "%Y-%m-%d %H:%M").date()
        except ValueError:
            continue

        if flight_date < today:
            old_ids.append(flight_id)

    for flight_id in old_ids:
        cursor.execute("""
            DELETE FROM flights
            WHERE id = ?
        """, (flight_id,))

    conn.commit()
    conn.close()