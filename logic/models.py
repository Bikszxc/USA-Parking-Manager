from db.database import get_connection

conn = get_connection()
cursor = conn.cursor()

# Add New Car Owner
def new_car_owner(owner_name, email, owner_type, contact_number):
    try:
        cursor.execute("INSERT INTO car_owners (owner_name, email, type, contact_number) VALUES (?, ?, ?, ?)",
                       (owner_name, email, owner_type, contact_number))

        conn.commit()

        return True
    except Exception as e:
        print("Error Occurred!", e)

    return False

# Fetch All Car Owners
def get_car_owners():
    try:
        cursor.execute("SELECT * FROM car_owners")
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

