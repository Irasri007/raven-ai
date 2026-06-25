# auth.py

import bcrypt
from datetime import datetime
from database import get_connection

def register_user(username, email, password):
    conn = get_connection()
    cursor = conn.cursor()

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    try:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )
        conn.commit()
        print(f"✅ User '{username}' registered successfully.")
        return True
    except Exception as e:
        print(f"❌ Registration failed: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()  # pyodbc doesn't support dictionary=True

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()

    if row:
        # Map columns manually
        columns = [column[0] for column in cursor.description]
        user = dict(zip(columns, row))

        if bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
            cursor.execute(
                "UPDATE users SET last_login = ? WHERE id = ?",
                (datetime.now(), user["id"])
            )
            conn.commit()
            print(f"✅ Welcome back, {username}!")
            cursor.close()
            conn.close()
            return user

    print("❌ Invalid username or password.")
    cursor.close()
    conn.close()
    return None