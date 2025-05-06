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

def account_deletion(username: str, master_password: str):
    try:
        if check_master_password(master_password):
            cursor.execute("DELETE FROM admins WHERE username = ?", (username,))
            conn.commit()
            return cursor.rowcount == 1
    except Exception as error:
        print(f"Error occurred during account deletion: {error}")

    return False

def account_login(username: str, password: str) -> bool:
    try:
        cursor.execute("SELECT password_hash FROM admins WHERE username = ?", (username,))
        result = cursor.fetchone()

        if not result:
            return False

        stored_hash = result[0].encode()
        return bcrypt.checkpw(password.encode(), stored_hash)
    except Exception as error:
        print(f"Error occurred during account login: {error}")
        return False