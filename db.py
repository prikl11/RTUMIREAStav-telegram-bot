import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        group_name TEXT,
        group_id INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bot_usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        command TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()

def log_usage(command: str):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO bot_usage (command) VALUES (?)
    """, (command,) )
    conn.commit()
    conn.close()

def get_count_command_usage():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM bot_usage")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_command_usage_number():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT command, COUNT(*) FROM bot_usage GROUP BY command")
    result = {command: count for command, count in cursor.fetchall()}
    conn.close()
    return result

def read_users():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_users_number_by_groups():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT group_name, COUNT(*) FROM users GROUP BY group_name")
    result = {group: count for group, count in cursor.fetchall()}
    conn.close()
    return result

def get_usage(period: str) -> int:
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    if period == "day":
        cursor.execute("SELECT COUNT(*) FROM bot_usage WHERE DATE(timestamp) = DATE('now')")
    if period == "week":
        cursor.execute("SELECT COUNT(*) FROM bot_usage WHERE DATE(timestamp) >= DATE('now', '-7 days')")
    if period == "month":
        cursor.execute("SELECT COUNT(*) FROM bot_usage WHERE DATE(timestamp) >= DATE('now', '-1 month')")

    count = cursor.fetchone()[0]
    conn.close()
    return count

def set_user_group_db(user_id: int, group_name: str, group_id: int):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (user_id, group_name, group_id)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            group_name=excluded.group_name,
            group_id=excluded.group_id
    """, (user_id, group_name, group_id))
    conn.commit()
    conn.close()

def get_user_group_db(user_id: int):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT group_name, group_id FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"group_name": row[0], "group_id": row[1]}
    return None
