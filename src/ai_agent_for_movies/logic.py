from .database import get_connection


def add_movie(title: str) -> None:
    """Добавляет фильм в базу данных."""
    with get_connection() as conn:
        conn.execute("INSERT INTO movies (title) VALUES (?)", (title,))


def list_movies() -> list:
    """Возвращает список всех фильмов из базы."""
    with get_connection() as conn:
        cursor = conn.execute("SELECT id, title, status FROM movies")
        return cursor.fetchall()


def done_movie(movie_id: int) -> None:
    """Меняет статус фильма на 'Просмотрено' по его ID."""
    with get_connection() as conn:
        # Проверяем, существует ли такой фильм
        movie = conn.execute(
            "SELECT id FROM movies WHERE id = ?", (movie_id,)
        ).fetchone()
        if not movie:
            raise IndexError  # Если нет, вызываем ошибку
        conn.execute(
            "UPDATE movies SET status = 'Просмотрено' WHERE id = ?", (movie_id,)
        )


def get_help() -> str:
    """Возвращает текст справки."""
    return """
Команды:
  add  — добавить фильм
  list — показать фильмы
  done — отметить просмотренным (по ID)
  help — справка
  exit — выход
"""
