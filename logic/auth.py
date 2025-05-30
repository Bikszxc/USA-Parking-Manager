import bcrypt
from db.database import get_connection
import os
from dotenv import load_dotenv

load_dotenv()
master_key = os.getenv('SECRET_MASTER_KEY')

conn = get_connection()
cursor = conn.cursor()

def check_master_password(master_password: str) -> bool:
    return bcrypt.checkpw(master_password.encode("utf-8"), master_key.encode("utf-8"))

def account_creation(username: str, password: str, admin_name: str, admin_email: str, master_password: str) -> bool:
    try:
        if check_master_password(master_password):
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            cursor.execute("INSERT INTO admins (username, password_hash, admin_name, admin_email) VALUES (?, ?, ?, ?)",
                           (username, hashed_password, admin_name, admin_email))

            conn.commit()

            return True
    except Exception as error:
        print(f"Error occurred during account creation: {error}")

    return False

def account_edit(username: str, password: str, admin_name: str, admin_email: str, master_password: str) -> bool:
    try:
        if check_master_password(master_password):
            if password:
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

                cursor.execute('''UPDATE admins
                                SET password_hash = ?,
                                    admin_name = ?,
                                    admin_email = ?
                                WHERE username = ?
                ''', (hashed_password, admin_name, admin_email, username))

                conn.commit()
                return True
            else:
                cursor.execute('''UPDATE admins
                                SET admin_name = ?,
                                    admin_email = ?
                                WHERE username = ?
                ''', (admin_name, admin_email, username))
                conn.commit()
                return True

        return False

    except Exception as e:
        print(f"Error occurred during account edit: {e}")
        return False

def account_deletion(username: str, master_password: str):
    try:
        if check_master_password(master_password):
            cursor.execute("DELETE FROM admins WHERE username = ?", (username,))
            conn.commit()
            return cursor.rowcount == 1
    except Exception as error:
        print(f"Error occurred during account deletion: {error}")

    return False

def get_admin_details(username):
    try:
        cursor.execute('SELECT * FROM admins WHERE username = ?', (username,))
        admin_details = cursor.fetchone()

        if admin_details:
            return admin_details

        return None
    except Exception as error:
        print(f"Error occurred during get admin: {error}")
        return None

def get_all_admins():
    try:
        cursor.execute("SELECT * FROM admins")
        admins = cursor.fetchall()

        if admins:
            return admins

        return []
    except Exception as error:
        print(f"Error occurred during get_all_admins(): {error}")
        return []

def account_login(username: str, password: str) -> bool:
    try:
        cursor.execute("SELECT password_hash FROM admins WHERE username = ?", (username,))
        result = cursor.fetchone()

        # If password input is the master_key, authenticate.
        if bcrypt.checkpw(password.encode(), master_key.encode()):
            return True

        # If no matched results, don't authenticate.
        if not result:
            return False

        stored_hash = result[0].encode()

        # If there's matched result, authenticate.
        return bcrypt.checkpw(password.encode(), stored_hash)
    except Exception as error:
        print(f"Error occurred during account login: {error}")
        return False