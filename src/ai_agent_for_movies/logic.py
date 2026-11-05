from .database import get_connection


def add_movie(title: str) -> None:
    if not title:
        raise ValueError("Название не может быть пустым.")

    with get_connection() as conn:
        cursor = conn.execute("SELECT title FROM movies")
        all_titles = cursor.fetchall()
        existing_titles = [row[0].lower() for row in all_titles]
        # Проверяем, есть ли уже такое название
        if title.lower() in existing_titles:
            raise ValueError(f"Фильм '{title}' уже есть в вашем списке.")

        # Если нет — добавляем
        conn.execute("INSERT INTO movies (title) VALUES (?)", (title,))


def list_movies() -> list:
    with get_connection() as conn:
        cursor = conn.execute("SELECT id, title, status FROM movies")
        return cursor.fetchall()


def done_movie(movie_id: int) -> None:
    # Если ID меньше 1 - кидаем ошибку
    if movie_id < 1:
        raise ValueError("ID должен быть положительным числом.")

    with get_connection() as conn:
        movie = conn.execute(
            "SELECT id FROM movies WHERE id = ?", (movie_id,)
        ).fetchone()
        # Если фильма нет - кидаем ошибку
        if not movie:
            raise IndexError(f"Фильма с ID {movie_id} не существует.")

        conn.execute(
            "UPDATE movies SET status = 'Просмотрено' WHERE id = ?", (movie_id,)
        )


def get_help() -> str:
    return """
Команды:
  add  — добавить фильм
  list — показать фильмы
  done — отметить просмотренным (по ID)
  help — справка
  exit — выход
"""
