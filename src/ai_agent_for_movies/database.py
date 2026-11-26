import sqlite3

# По умолчанию используем movies.db, но тесты смогут это переопределить
DB_NAME = "movies.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'В планах'
            )
        """)
