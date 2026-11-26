import sqlite3

import pytest

from src.ai_agent_for_movies.cli import StorageError, run
from src.ai_agent_for_movies.logic import (
    add_movie,
    delete_movie,
    done_movie,
    list_movies,
)


@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch, tmp_path):
    # tmp_path — это уникальная временная папка, которую создает pytest для каждого теста
    test_db_path = tmp_path / "test_movies.db"

    # Создаем функцию подключения к этой временной базе
    def mock_get_connection():
        return sqlite3.connect(test_db_path)

    # Подменяем get_connection во всех модулях
    monkeypatch.setattr(
        "src.ai_agent_for_movies.database.get_connection", mock_get_connection
    )
    monkeypatch.setattr(
        "src.ai_agent_for_movies.logic.get_connection", mock_get_connection
    )

    # Создаем таблицу
    with sqlite3.connect(test_db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'В планах'
            )
        """)

    yield


# тест логики


def test_add_movie():
    add_movie("Тестовый фильм")
    movies = list_movies()
    assert len(movies) == 1
    assert movies[0][1] == "Тестовый фильм"
    assert movies[0][2] == "В планах"


def test_add_duplicate_movie():
    add_movie("Дюна")
    with pytest.raises(ValueError):
        add_movie("Дюна")


def test_done_movie():
    add_movie("Интерстеллар")
    movie_id = list_movies()[0][0]
    done_movie(movie_id)
    assert list_movies()[0][2] == "Просмотрено"


def test_done_nonexistent_movie():
    with pytest.raises(IndexError):
        done_movie(999)


def test_delete_movie():
    add_movie("Удаляемый фильм")
    movie_id = list_movies()[0][0]
    delete_movie(movie_id)
    assert len(list_movies()) == 0


# тест CLI


def test_cli_add_and_list(monkeypatch, capsys):
    # Имитируем ввод: add -> "Дюна" -> list -> exit
    inputs = iter(["add", "Дюна", "list", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    run()  # Запускаем программу

    captured = capsys.readouterr()
    assert "Фильм 'Дюна' добавлен." in captured.out
    # Проверяем, что в выводе есть название фильма и его статус, не привязываясь к цифре
    assert "Дюна [В планах]" in captured.out


def test_cli_delete(monkeypatch, capsys):
    # Сначала добавим фильм
    add_movie("Фильм для удаления")
    # Узнаем, какой ID ему присвоила база
    movie_id = list_movies()[0][0]

    # Передаем этот ID в программу
    inputs = iter(["delete", str(movie_id), "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    run()

    captured = capsys.readouterr()
    assert f"Фильм с ID {movie_id} удален." in captured.out


def test_cli_invalid_input(monkeypatch, capsys):
    # Имитируем ввод: done -> "abc" (ошибка) -> неизвестная команда -> exit
    inputs = iter(["done", "abc", "some_command", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    run()

    captured = capsys.readouterr()
    assert "invalid literal for int()" in captured.out
    assert "Неизвестная команда" in captured.out


def test_cli_overflow_error(monkeypatch, capsys):
    # Имитируем ввод огромного числа
    inputs = iter(["done", "999999999999999999999999", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    run()

    captured = capsys.readouterr()
    assert "Число слишком большое" in captured.out


def test_cli_empty_title(monkeypatch, capsys):
    # Проверяем пустой ввод при добавлении
    inputs = iter(["add", "", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    run()

    captured = capsys.readouterr()
    assert "Название не может быть пустым." in captured.out


def test_add_empty_title():
    """Тест добавления пустого названия (проверка на ошибку)."""
    with pytest.raises(ValueError, match="Название не может быть пустым."):
        add_movie("")


def test_add_duplicate_via_cli(monkeypatch, capsys):
    """Тест добавления дубликата через интерфейс."""
    add_movie("Дюна")  # Добавляем первый раз напрямую
    inputs = iter(["add", "Дюна", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    run()
    captured = capsys.readouterr()
    assert "Фильм 'Дюна' уже есть в вашем списке." in captured.out


def test_done_negative_id():
    """Тест отрицательного ID."""
    with pytest.raises(ValueError, match="ID должен быть положительным числом."):
        done_movie(-1)


def test_cli_help(monkeypatch, capsys):
    """Тест вывода справки."""
    inputs = iter(["help", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    run()
    captured = capsys.readouterr()
    assert "Команды:" in captured.out


def test_main_file(monkeypatch):
    """Тест запуска через файл __main__.py."""
    inputs = iter(["exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    import src.ai_agent_for_movies.__main__ as main_module

    # Просто проверяем, что импорт и вызов не падают
    main_module.run()


def test_cli_list_empty(monkeypatch, capsys):
    """Проверяет ветку, когда список фильмов пуст."""
    inputs = iter(["list", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    run()
    captured = capsys.readouterr()
    assert "Список фильмов пуст." in captured.out


def test_cli_delete_command(monkeypatch, capsys):
    """Проверяет команду delete именно через интерфейс."""
    add_movie("Фильм на удаление")
    movie_id = list_movies()[0][0]

    inputs = iter(["delete", str(movie_id), "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    run()
    captured = capsys.readouterr()
    assert f"Фильм с ID {movie_id} удален." in captured.out


def test_cli_keyboard_interrupt(monkeypatch, capsys):
    """Проверяет обработку Ctrl+C."""
    # При вводе команды выбрасываем KeyboardInterrupt (как будто нажали Ctrl+C)
    monkeypatch.setattr(
        "builtins.input", lambda _: (_ for _ in ()).throw(KeyboardInterrupt)
    )
    run()
    captured = capsys.readouterr()
    assert "Выход из программы." in captured.out


def test_cli_unexpected_error(monkeypatch, capsys):
    """Проверяет обработку непредвиденной ошибки (except Exception)."""

    # Имитируем ошибку в базе данных, подменяя функцию list_movies
    def mock_error():
        raise StorageError("Тестовая ошибка хранилища")

    # Подменяем функцию list_movies на "сломанную"
    monkeypatch.setattr("src.ai_agent_for_movies.cli.list_movies", mock_error)

    inputs = iter(["list", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    run()

    captured = capsys.readouterr()
    # Проверяем, что программа не упала, а вывела наше сообщение
    assert "Ошибка работы с хранилищем" in captured.out
    assert "Программа продолжает работу." in captured.out


def test_cli_broken_db(monkeypatch, capsys, tmp_path):
    """Проверяет обработку ошибки при поврежденной базе данных."""
    # Создаем битый файл базы данных во временной папке
    bad_db = tmp_path / "broken.db"
    bad_db.write_text("broken sqlite database")

    # Создаем функцию, которая выбрасывает ошибку DatabaseError
    def mock_init_db():
        raise sqlite3.DatabaseError("file is not a database")

    # Подменяем init_db в cli.py на нашу "сломанную" функцию
    monkeypatch.setattr("src.ai_agent_for_movies.cli.init_db", mock_init_db)

    # Имитируем ввод (он не должен понадобиться, так как программа должна упасть)
    inputs = iter(["exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    # Запускаем программу
    run()

    captured = capsys.readouterr()
    # Проверяем, что программа вежливо сообщила об ошибке
    assert "Критическая ошибка" in captured.out
    assert "не удалось открыть базу данных" in captured.out
