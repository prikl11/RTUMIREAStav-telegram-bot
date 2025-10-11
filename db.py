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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS preps (
        prep_id INTEGER PRIMARY KEY,
        prep_name TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS meta (
        key TEXT PRIMARY KEY,
        value TEXT
    )
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

def update_meta():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('preps_last_update', datetime('now'))")
    conn.commit()
    conn.close()

def check_meta():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM meta WHERE key='preps_last_update'")
    last_update = cursor.fetchone()
    conn.close()
    return last_update

def get_preps_id(prep_name: str):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT prep_id FROM preps WHERE prep_name LIKE ?", (f"%{prep_name}%",))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None