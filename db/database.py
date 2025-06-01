import sqlite3
import os
from datetime import datetime, timezone, timedelta

os.makedirs('./data', exist_ok=True)

DB_PATH = os.path.join("data", "parking.db")
print(DB_PATH)

def get_connection():
    app_data_dir = os.path.join(os.path.expanduser("~"), "USAParkingManager")
    os.makedirs(app_data_dir, exist_ok=True)

    db_path = os.path.join(app_data_dir, "database.db")
    return sqlite3.connect(db_path)

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

def clear_past_reservations():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM reservations')
    reservations = cursor.fetchall()

    for res in reservations:
        reservation_date = datetime.strptime(res[7], "%m-%d-%Y")

        if datetime.now().date() > reservation_date.date():
            cursor.execute('DELETE FROM reservations WHERE id=?', (res[0],))

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
        contact_number TEXT
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
        type TEXT NOT NULL,
        email TEXT NOT NULL,
        contact_number TEXT NOT NULL,
        plate_number TEXT NOT NULL,
        vehicle_type TEXT,
        reservation_date TEXT,
        reservation_time TEXT,
        status TEXT NOT NULL DEFAULT 'PENDING',
        assigned_slot TEXT,
        is_late BOOLEAN DEFAULT 0,
        grace_period_until TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accepted_reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slot_number TEXT NOT NULL,
        reservation_id TEXT,
        FOREIGN KEY (reservation_id) REFERENCES reservations(id)
        )
    ''')

    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS accept_reservations
            AFTER UPDATE OF status
            ON reservations
            FOR EACH ROW
            WHEN NEW.status = 'APPROVED'
        BEGIN
            INSERT INTO accepted_reservations (slot_number, reservation_id)
            VALUES (NEW.assigned_slot, NEW.id);
        END
    ''')


    conn.commit()
    conn.close()

    create_parking_slots()
    clear_past_reservations()