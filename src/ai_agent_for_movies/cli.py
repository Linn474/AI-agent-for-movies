from .database import init_db
from .logic import add_movie, done_movie, get_help, list_movies


def run() -> None:
    init_db()  # Создаем базу при запуске
    print("Добро пожаловать в ИИ-агент 'Помощник по фильмам'!")
    print(get_help())

    while True:
        try:
            command = input("> ").strip().lower()

            if command == "add":
                title = input("Введите название фильма > ").strip()
                if not title:
                    print("Ошибка: Название не может быть пустым.")
                    continue
                add_movie(title)
                print(f"Фильм '{title}' добавлен.")

            elif command == "list":
                movies = list_movies()
                if not movies:
                    print("Список фильмов пуст.")
                else:
                    print("\nСписок фильмов:")
                    for m in movies:
                        print(f"{m[0]}. {m[1]} [{m[2]}]")
                    print()

            elif command == "done":
                try:
                    movie_id = int(input("Введите ID фильма > "))
                    done_movie(movie_id)
                    print("Статус изменен на 'Просмотрено'.")
                except ValueError:
                    print("Ошибка: ID должен быть числом.")
                except IndexError:
                    print("Ошибка: Фильма с таким ID нет.")

            elif command == "help":
                print(get_help())

            elif command == "exit":
                print("До свидания!")
                break

            else:
                print("Неизвестная команда. Введите 'help'.")

        except KeyboardInterrupt:
            print("\nВыход.")
            break
