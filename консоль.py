import os
import time


def clear_console():
    os.system('cls')


def main():
    clear_console()
    while True:
        question = "Ты - человек?"
        answer = input(f"{question}\nВаш ответ: ").strip().lower()

        if answer == "да":
            clear_console()
            print("Сосал??)))")
            print("Да.")
            break
        elif answer == "нет":
            print("Скажи правду.")
            time.sleep(2)
            clear_console()
        else:
            print("Пожалуйста, ответь только да или нет.")
            time.sleep(2)
            clear_console()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear_console()
        print("Закрыто")
