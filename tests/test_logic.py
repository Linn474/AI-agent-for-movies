import pytest
import os
from src.ai_agent_for_movies.logic import add_movie, list_movies, done_movie, delete_movie
from src.ai_agent_for_movies.database import init_db, get_connection

#создает временную базу данных для каждого теста
@pytest.fixture(autouse=True)
def setup_test_db():
    # Перед тестом создаем базу
    init_db()
    yield
    # После теста (независимо от результата) очищаем базу
    with get_connection() as conn:
        conn.execute("DELETE FROM movies")

def test_add_movie():
    """Тест добавления фильма."""
    add_movie("Тестовый фильм")
    movies = list_movies()
    assert len(movies) == 1
    assert movies[0][1] == "Тестовый фильм"
    assert movies[0][2] == "В планах"

def test_add_duplicate_movie():
    """Тест добавления дубликата (должна быть ошибка)."""
    add_movie("Дюна")
    with pytest.raises(ValueError):
        add_movie("Дюна")

def test_done_movie():
    """Тест изменения статуса."""
    add_movie("Интерстеллар")
    movie_id = list_movies()[0][0]
    done_movie(movie_id)
    movies = list_movies()
    assert movies[0][2] == "Просмотрено"

def test_done_nonexistent_movie():
    """Тест изменения статуса несуществующего фильма."""
    with pytest.raises(IndexError):
        done_movie(999)

def test_delete_movie():
    """Тест удаления фильма."""
    add_movie("Удаляемый фильм")
    movie_id = list_movies()[0][0]
    delete_movie(movie_id)
    movies = list_movies()
    assert len(movies) == 0