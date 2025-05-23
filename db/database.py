import sqlite3
import os

DB_PATH = os.path.join("data", "parking.db")
print(DB_PATH)

def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def create_parking_slots():
    connection = get_connection()
    cursor = connection.cursor()

    letters = ["A", "B", "C", "D", "E"]

    cursor.execute('SELECT * FROM parking_slots')
    parking_slots = cursor.fetchall()

    if not parking_slots:
        for i in range(1, 6):
            for letter in letters:
                slot = f"{i}{letter}"
                cursor.execute("INSERT INTO parking_slots (slot_number) VALUES (?)", (slot,))
                connection.commit()

    connection.close()



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
        vehicle_type TEXT NOT NULL,
        registration_date TEXT NOT NULL,
        expiration_date TEXT NOT NULL,
        FOREIGN KEY (owner_id) REFERENCES car_owners(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parking_slots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slot_number TEXT UNIQUE NOT NULL,
        is_occupied BOOLEAN DEFAULT 0,
        vehicle_type TEXT,
        owner_name TEXT,
        plate_number TEXT,
        type TEXT,
        contact_number TEXT,
        reservation_id INTEGER,
        reservation_dt TEXT,
        FOREIGN KEY (reservation_id) REFERENCES reservations(id)
        )
    ''')

    cursor.execute('''
                   CREATE TRIGGER IF NOT EXISTS clear_parking_slot_fields
                       AFTER UPDATE OF is_occupied
                       ON parking_slots
                       FOR EACH ROW
                       WHEN NEW.is_occupied = 0
                   BEGIN
                       UPDATE parking_slots
                       SET owner_name     = NULL,
                           plate_number   = NULL,
                           vehicle_type   = NULL,
                           type = NULL,
                           contact_number = NULL
                       WHERE id = NEW.id;
                   END;
                   ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        contact_number TEXT NOT NULL,
        plate_number TEXT NOT NULL,
        vehicle_type TEXT,
        reservation_date TEXT,
        reservation_time TEXT,
        status TEXT NOT NULL DEFAULT 'PENDING'
        )
    ''')

    conn.commit()
    conn.close()

    create_parking_slots()