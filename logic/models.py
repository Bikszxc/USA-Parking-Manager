from db.database import get_connection
from datetime import datetime, timezone, timedelta

ph_offset = timezone(timedelta(hours=8))
ph_time = datetime.now(ph_offset)

conn = get_connection()
cursor = conn.cursor()

def new_admin_log(admin_name, action):
    try:
        cursor.execute("SELECT id FROM admins WHERE username = ?", (admin_name,))
        admin_id = cursor.fetchone()

        cursor.execute("INSERT INTO admin_logs (admin_id, action, timestamp) VALUES (?, ?, ?)", (admin_id[0], action, ph_time))
        conn.commit()
    except Exception as e:
        print(f"Error Occurred! {e}")

def create_reservation(name, type, email, contact_number, plate_number, vehicle_type, reservation_date, reservation_time):
    try:
        api_conn = get_connection()
        api_cursor = api_conn.cursor()

        reservation_date = datetime.strptime(reservation_date, "%Y-%m-%d")
        reservation_time = datetime.strptime(reservation_time, "%H:%M")

        api_cursor.execute("INSERT INTO reservations (name, type, email, contact_number, plate_number, vehicle_type, reservation_date, reservation_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       (name, type, email, contact_number, plate_number, vehicle_type, reservation_date.strftime("%m-%d-%Y"), reservation_time.strftime("%H:%M")))

        api_conn.commit()

        return True
    except Exception as e:
        print(f"Error Occurred! {e}")
        return False

# Add New Car Owner
def new_car_owner(owner_name, email, owner_type, contact_number, refresh_callback=None) -> bool:
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


# Park Vehicle to a Parking Slot
def park_vehicle(slot_number, vehicle_type, owner_name, plate_number, status_type, contact_number) -> bool:
    try:
        cursor.execute('''
                       UPDATE parking_slots
                       SET is_occupied    = 1,
                           vehicle_type   = ?,
                           owner_name     = ?,
                           plate_number   = ?,
                           type           = ?,
                           contact_number = ?
                       WHERE slot_number = ?
                       ''', (vehicle_type, owner_name, plate_number, status_type, contact_number, slot_number))

        conn.commit()

        # new_admin_log(admin_name, f"Parked {plate_number} in Slot {slot_number}")

        return True
    except Exception as e:
        print("Error Occurred!", e)
        return False


def unpark_vehicle(slot) -> bool:
    try:
        cursor.execute("SELECT is_occupied FROM parking_slots WHERE slot_number = ?", (slot,))
        slot_occupied = cursor.fetchone()[0]

        if slot_occupied == 1:
            cursor.execute('''
                           UPDATE parking_slots
                           SET is_occupied = 0
                           WHERE slot_number = ?
                           ''', (slot,))

            conn.commit()

            return True

        return False
    except Exception as e:
        print("Error Occurred!", e)
        return False


# Assign Vehicle to Car Owner
def assign_vehicle(owner_name, plate_number, vehicle_type) -> bool:
    try:
        cursor.execute("SELECT id FROM car_owners WHERE owner_name= ?", (owner_name,))
        owner_id = cursor.fetchone()

        if owner_id:
            cursor.execute("INSERT INTO registered_cars (owner_id, plate_number, vehicle_type) VALUES (?, ?, ?)",
                           (owner_id[0], plate_number, vehicle_type,))

            conn.commit()

            return True

        return False
    except Exception as e:
        print("Error Occurred!", e)
        return False

def accept_reservation(reservation_id, slot_number):
    try:
        cursor.execute('''UPDATE reservations
                        SET status = ?,
                            assigned_slot = ?
                        WHERE id = ?
        ''', ("APPROVED", slot_number, reservation_id))
        conn.commit()

        return True
    except Exception as e:
        print("Error Occurred!", e)
        return False

def reject_reservation(reservation_id):
    try:
        cursor.execute('''UPDATE reservations
                        SET status = ?
                        WHERE id = ?
        ''', ("REJECTED", reservation_id))
        conn.commit()

        return True
    except Exception as e:
        print("Error Occurred!", e)
        return False

def cancel_accepted_reservation(reservation_id):
    try:
        cursor.execute('DELETE FROM accepted_reservations WHERE reservation_id = ?', (reservation_id,))
        conn.commit()

        return True
    except Exception as e:
        print("Error Occurred!", e)
        return False


def update_reservation_late_status(reservation_id, grace_period_str):
    try:
        cursor.execute('''UPDATE reservations
                        SET is_late = ?,
                            grace_period_until = ?
                        WHERE id = ?
        ''', (1, grace_period_str, reservation_id))

        if cursor.rowcount == 0:
            return False

        conn.commit()
        return True
    except Exception as e:
        print("Error Occurred!", e)
        return False

# ================== DELETION =================== #

def delete_car_owner(owner_name) -> bool:
    try:
        cursor.execute('SELECT id FROM car_owners WHERE owner_name = ?', (owner_name,))
        owner_id = cursor.fetchone()

        if owner_id:
            cursor.execute('DELETE FROM car_owners WHERE id = ?', (owner_id[0],))
            conn.commit()
            return True

        return False
    except Exception as e:
        print("Error Occurred!", e)
        return False

def unassign_vehicle(plate_number) -> bool:
    try:
        cursor.execute('''DELETE FROM registered_cars WHERE plate_number = ?''', (plate_number,))

        if cursor.rowcount == 0:
            return False
        conn.commit()
        return True
    except Exception as e:
        print("Error Occurred!", e)
        return False

# ==================== FETCHES ===================== #

def get_vehicles():
    try:
        cursor.execute("SELECT * FROM registered_cars")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error Occurred! {e}")
        return None

def get_vehicle_owner(owner_id):
    try:
        cursor.execute("SELECT owner_name FROM car_owners WHERE id = ?", (owner_id,))
        owner_name = cursor.fetchone()

        if owner_name:
            return owner_name[0]

        return None
    except Exception as e:
        print(f"Error Occurred! {e}")
        return None

def check_plate_number(plate_number) -> bool:
    try:
        cursor.execute("SELECT id FROM registered_cars WHERE plate_number =?", (plate_number,))
        plate_number = cursor.fetchone()

        if plate_number:
            return True

        return False
    except Exception as e:
        print(f"Error Occurred! {e}")
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

def get_reservations():
    try:
        cursor.execute("SELECT * FROM reservations")
        reservations = cursor.fetchall()

        if reservations:
            return reservations

        return None
    except Exception as e:
        print(f"Error Occurred! {e}")
        return None

def get_res_id_details(slot_number):
    try:
        current_datetime = ph_time
        current_date =  current_datetime.strftime("%m-%d-%Y")
        current_time = current_datetime.strftime("%H:%M")

        cursor.execute('''
            SELECT r.* FROM reservations r
            JOIN accepted_reservations ar ON r.id = ar.reservation_id
            WHERE ar.slot_number = ?
            AND (
                r.reservation_date > ? OR
                (r.reservation_date = ? AND r.reservation_time >= ?)
            )
            ORDER BY r.reservation_date ASC, r.reservation_time ASC
            LIMIT 1
        ''', (slot_number, current_date, current_date, current_time))

        next_reservation = cursor.fetchone()

        if next_reservation:
            return next_reservation

        return None

    except Exception as e:
        print(f"Error Occurred! {e}")
        return None

def get_owner(owner_name: str):
    try:
        cursor.execute("SELECT id, owner_name, type, contact_number, email FROM car_owners WHERE owner_name = ? COLLATE NOCASE",
                       (owner_name,))
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
        cursor.execute("SELECT id FROM car_owners WHERE owner_name = ? COLLATE NOCASE", (owner_name,))
        owner_id = cursor.fetchone()
        owner_id = owner_id[0]

        cursor.execute("SELECT * FROM registered_cars WHERE owner_id = ?", (owner_id,))
        return cursor.fetchall()
    except Exception as e:
        print("Error Occurred!", e)
        return None


def get_vehicle_type(plate_number):
    try:
        cursor.execute("SELECT vehicle_type FROM registered_cars WHERE plate_number = ?", (plate_number,))
        return cursor.fetchone()
    except Exception as e:
        print("Error Occurred!", e)
        return None

# Fetch all Parking Slots
def get_parking_slots():
    try:
        cursor.execute("SELECT * FROM parking_slots")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error Occurred!", e)
        return None

def get_parkslot_info(slot_number):
    try:
        cursor.execute("SELECT * FROM parking_slots WHERE slot_number = ?", (slot_number,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error Occurred!", e)
        return None

def edit_car_owner(owner_name, owner_type, owner_email, owner_contact):
    try:
        cursor.execute('''UPDATE car_owners
                        SET type = ?,
                            email = ?,
                            contact_number = ?
                        WHERE owner_name = ?
        ''', (owner_type, owner_email, owner_contact, owner_name))

        if cursor.rowcount == 0:
            return False

        conn.commit()
        return True
    except Exception as e:
        print(f"Error Occurred!", e)
        return False

