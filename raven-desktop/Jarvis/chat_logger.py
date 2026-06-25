# chat_logger.py

from database import get_connection

def log_chat(user_id, command, response):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_logs (user_id, command, response) VALUES (?, ?, ?)",
        (user_id, command, response)
    )
    conn.commit()
    cursor.close()
    conn.close()

def get_user_chats(user_id, limit=10):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT command, response, timestamp
        FROM chat_logs
        WHERE user_id = ?
        ORDER BY timestamp DESC
    """, (user_id,))
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    cursor.close()
    conn.close()
    return [dict(zip(columns, row)) for row in rows]

def get_all_user_stats():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.username, u.email, u.last_login, COUNT(c.id) AS total_commands
        FROM users u
        LEFT JOIN chat_logs c ON u.id = c.user_id
        GROUP BY u.id, u.username, u.email, u.last_login
        ORDER BY total_commands DESC
    """)
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    cursor.close()
    conn.close()
    return [dict(zip(columns, row)) for row in rows]