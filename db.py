import sqlite3
from contextlib import contextmanager

from constants import DB_PATH


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn.cursor()
    finally:
        conn.close()


@contextmanager
def get_db_commit():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn.cursor()
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_db_commit() as cursor:
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


def log_usage(command: str):
    with get_db_commit() as cursor:
        cursor.execute("""
        INSERT INTO bot_usage (command) VALUES (?)
        """, (command,) )


def get_count_command_usage():
    with get_db() as cursor:
        cursor.execute("SELECT COUNT(*) FROM bot_usage")   
        return cursor.fetchone()[0]
    

def get_command_usage_number():
    with get_db() as cursor:
        cursor.execute("SELECT command, COUNT(*) FROM bot_usage GROUP BY command")
        return {command: count for command, count in cursor.fetchall()}
    

def read_users():
    with get_db() as cursor:
        cursor.execute("SELECT COUNT(*) FROM users")
        return cursor.fetchone()[0]


def get_users_number_by_groups():
    with get_db() as cursor:
        cursor.execute("SELECT group_name, COUNT(*) FROM users GROUP BY group_name")
        return {group: count for group, count in cursor.fetchall()}
    

def get_usage(period: str) -> int:
    with get_db() as cursor:
        if period == "day":
            cursor.execute("SELECT COUNT(*) FROM bot_usage WHERE DATE(timestamp) = DATE('now')")
        elif period == "week":
            cursor.execute("SELECT COUNT(*) FROM bot_usage WHERE DATE(timestamp) >= DATE('now', '-7 days')")
        elif period == "month":
            cursor.execute("SELECT COUNT(*) FROM bot_usage WHERE DATE(timestamp) >= DATE('now', '-1 month')")

        return cursor.fetchone()[0]


def set_user_group_db(user_id: int, group_name: str, group_id: int):
    with get_db_commit() as cursor:
        cursor.execute("""
            INSERT INTO users (user_id, group_name, group_id)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                group_name=excluded.group_name,
                group_id=excluded.group_id
        """, (user_id, group_name, group_id))


def get_user_group_db(user_id: int):
    with get_db() as cursor:
        cursor.execute("SELECT group_name, group_id FROM users WHERE user_id=?", (user_id,))
        row = cursor.fetchone()
        if row:
            return {"group_name": row[0], "group_id": row[1]}
        return None


def update_meta():
    with get_db_commit() as cursor:
        cursor.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('preps_last_update', datetime('now'))")


def check_meta():
    with get_db() as cursor:
        cursor.execute("SELECT value FROM meta WHERE key='preps_last_update'")
        return cursor.fetchone()


def get_preps_id(prep_name: str):
    with get_db() as cursor:
        cursor.execute("SELECT prep_id, prep_name FROM preps")
        rows = cursor.fetchall()
        search = prep_name.strip().lower()
        for prep_id, name in rows:
            name_lower = name.lower()
            if name_lower == search or name_lower.startswith(search + " "):
                return prep_id
        return None