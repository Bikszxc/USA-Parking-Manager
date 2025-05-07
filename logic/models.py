from db.database import get_connection

conn = get_connection()
cursor = conn.cursor()

# Add New Car Owner
def new_car_owner(owner_name, email, owner_type, contact_number, refresh_callback=None):
    try:
        cursor.execute("INSERT INTO car_owners (owner_name, email, type, contact_number) VALUES (?, ?, ?, ?)",
                       (owner_name, email, owner_type, contact_number))

        conn.commit()

        if refresh_callback:
            refresh_callback()

        return True
    except Exception as e:
        print("Error Occurred!", e)

    return False

def record_found(owner_name: str = None):
    try:
        cursor.execute("SELECT * FROM car_owners WHERE owner_name = ?", (owner_name,))
        owner = cursor.fetchone()

        if owner:
            return True

        return False
    except Exception as e:
        print("Error Occurred!", e)
        return False

def get_owner(owner_name: str):
    try:
        cursor.execute("SELECT id, owner_name, type, contact_number FROM car_owners WHERE owner_name = ?", (owner_name,))
        return cursor.fetchone()
    except Exception as e:
        print("Error Occurred!", e)
        return None

# Fetch All Car Owners
def get_car_owners():
    try:
        cursor.execute("SELECT * FROM car_owners")
        return cursor.fetchall()
    except Exception as e:
        print("Error Occurred!", e)
        return None

# Fetch All Vehicles of Car Owner
def get_owner_vehicles(owner_name):
    try:
        cursor.execute("SELECT id FROM car_owners WHERE owner_name = ?", (owner_name,))
        owner_id = cursor.fetchone()
        owner_id = owner_id[0]

        cursor.execute("SELECT * FROM registered_cars WHERE owner_id = ?", (owner_id,))
        return cursor.fetchall()
    except Exception as e:
        print("Error Occurred!", e)
        return None

# Assign Vehicle to Car Owner
def assign_vehicle(owner_id, plate_number, vehicle_type):
    try:
        cursor.execute("INSERT INTO registered_cars (owner_id, plate_number, vehicle_type) VALUES (?, ?, ?)",
                       (owner_id, plate_number, vehicle_type))

        conn.commit()
    except Exception as e:
        print("Error Occurred!", e)

def get_vehicle_type(plate_number):
    try:
        cursor.execute("SELECT vehicle_type FROM registered_cars WHERE plate_number = ?", (plate_number,))
        return cursor.fetchone()
    except Exception as e:
        print("Error Occurred!", e)
        return None

# Park Vehicle to a Parking Slot
def park_vehicle(slot_number, vehicle_type, owner_name, plate_number, status_type, contact_number):
    try:
        cursor.execute('''
        UPDATE parking_slots
        SET is_occupied = 1,
            vehicle_type = ?,
            owner_name = ?,
            plate_number = ?,
            type = ?,
            contact_number = ?
        WHERE slot_number = ?
        ''', (vehicle_type, owner_name, plate_number, status_type, contact_number, slot_number))

        conn.commit()

        return True
    except Exception as e:
        print("Error Occurred!", e)
        return False

def unpark_vehicle(slot):
    try:
        cursor.execute('''
        UPDATE parking_slots
        SET is_occupied = 0
        WHERE slot_number = ?
        ''', (slot,))

        conn.commit()

        return True
    except Exception as e:
        print("Error Occurred!", e)
        return False
