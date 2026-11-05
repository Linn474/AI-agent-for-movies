from .database import init_db
from .logic import add_movie, done_movie, get_help, list_movies


def run() -> None:
    init_db()
    print("Добро пожаловать в ИИ-агент 'Помощник по фильмам'!")
    print(get_help())

    while True:
        try:
            command = input("> ").strip().lower()

            if command == "add":
                title = input("Введите название фильма > ").strip()
                try:
                    add_movie(title)
                    print(f"Фильм '{title}' добавлен.")
                except ValueError as e:
                    print(f"Ошибка: {e}")

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
                except ValueError as e:
                    print(
                        f"Ошибка: {e}"
                    )  # Ловит и буквы вместо ID, и отрицательные числа
                except IndexError as e:
                    print(f"Ошибка: {e}")  # Ловит несуществующий ID

            elif command == "help":
                print(get_help())

            elif command == "exit":
                print("До свидания!")
                break

            else:
                # Тоже можно сделать через raise, но проще просто вывести ошибку
                print("Ошибка: Неизвестная команда. Введите 'help' для справки.")

        except KeyboardInterrupt:
            print("\nВыход из программы.")
            break
