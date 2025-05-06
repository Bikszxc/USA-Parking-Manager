import sqlite3
import os

DB_PATH = os.path.join("data", "parking.db")
print(DB_PATH)

def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        admin_name TEXT NOT NULL,
        admin_email TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_id INTEGER NOT NULL,
        action TEXT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(admin_id) REFERENCES admins(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS car_owners (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        type TEXT NOT NULL,
        contact_number TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registered_cars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_id INTEGER,
        plate_number TEXT UNIQUE NOT NULL,
        car_type TEXT NOT NULL,
        FOREIGN KEY (owner_id) REFERENCES car_owners(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parking_slots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slot_number TEXT UNIQUE NOT NULL,
        is_occupied BOOLEAN DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parking_reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_id INTEGER,
        car_id INTEGER,
        slot_id INTEGER,
        date_reserved TEXT,
        status TEXT DEFAULT 'pending',
        FOREIGN KEY(owner_id) REFERENCES car_owners(id),
        FOREIGN KEY(car_id) REFERENCES registered_cars(id),
        FOREIGN KEY(slot_id) REFERENCES parking_slots(id)
        )
    ''')

    conn.commit()
    conn.close()