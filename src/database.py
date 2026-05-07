import sqlite3
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
                checked_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            flight.get("from"),
            flight.get("to"),
            flight.get("departure_time"),
            flight.get("arrival_time"),
            flight.get("price"),
            flight.get("duration"),
            flight.get("stops"),
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
            checked_at
        FROM flights
        WHERE departure = ? AND arrival = ?
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
            "checked_at": row[7],
        })

    return flights

def clean_old_flights():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM flights
        WHERE date(departure_time) < date('now')
    """)

    conn.commit()
    conn.close()

