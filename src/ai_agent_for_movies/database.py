import sqlite3

def get_connection():
    """Создает и возвращает подключение к базе данных SQLite."""
    return sqlite3.connect("movies.db")

def init_db():
    """Создает таблицу фильмов, если ее еще нет."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'В планах'
            )
        """)