import sqlite3

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
    conn.commit()
    conn.close()

def read_users():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
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