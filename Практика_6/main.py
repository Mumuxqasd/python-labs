from datetime import date

from exceptions import EntityNotFoundError, InvalidStatusError
from models import TaskStatus
from protocols import print_report_item
from services import TaskService, inspect_object


def read_int(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Введите целое число")


def read_date(prompt: str) -> date:
    while True:
        try:
            return date.fromisoformat(input(prompt).strip())
        except ValueError:
            print("Введите дату в формате ГГГГ-ММ-ДД")


def choose_status() -> TaskStatus:
    statuses = list(TaskStatus)
    for index, status in enumerate(statuses, 1):
        print(f"{index}. {status.value}")
    number = read_int("Новый статус: ")
    if number < 1 or number > len(statuses):
        raise ValueError("Нет такого статуса")
    return statuses[number - 1]


def print_all(service: TaskService) -> None:
    print("\nПРОЕКТЫ")
    for project in service.projects:
        print_report_item(project)
    print("\nПОЛЬЗОВАТЕЛИ")
    for user in service.users:
        print_report_item(user)
    print("\nЗАДАЧИ")
    for task in service.tasks:
        print_report_item(task)


def main() -> None:
    service = TaskService()

    while True:
        print("\n=== МЕНЕДЖЕР ЗАДАЧ ===")
        print("1. Добавить пользователя")
        print("2. Добавить проект")
        print("3. Добавить задачу")
        print("4. Удалить задачу")
        print("5. Найти задачу")
        print("6. Вывести все объекты")
        print("7. Изменить статус задачи")
        print("8. Назначить задачу пользователю")
        print("9. Показать просроченные задачи")
        print("10. Показать загрузку пользователей")
        print("11. Статистика")
        print("12. Интроспекция задачи")
        print("13. Демонстрация контекстного менеджера")
        print("0. Выход")
        choice = input("Выберите пункт: ").strip()

        try:
            if choice == "1":
                user = service.add_user(input("Имя: "))
                print("Создан:", user)
            elif choice == "2":
                project = service.add_project(input("Название проекта: "))
                print("Создан:", project)
            elif choice == "3":
                task = service.add_task(
                    input("Название задачи: "),
                    read_int("ID проекта: "),
                    read_date("Срок ГГГГ-ММ-ДД: "),
                )
                print("Создана:", task)
            elif choice == "4":
                service.delete_task(read_int("ID задачи: "))
                print("Задача удалена")
            elif choice == "5":
                print_report_item(service.find_task(read_int("ID задачи: ")))
            elif choice == "6":
                print_all(service)
            elif choice == "7":
                service.change_status(read_int("ID задачи: "), choose_status())
                print("Статус изменён")
            elif choice == "8":
                service.assign_task(
                    read_int("ID задачи: "), read_int("ID пользователя: ")
                )
            elif choice == "9":
                tasks = service.overdue_tasks()
                if not tasks:
                    print("Просроченных задач нет")
                for task in tasks:
                    print_report_item(task)
            elif choice == "10":
                for user, load in service.user_load():
                    print(f"{user.name}: {load} активных задач")
            elif choice == "11":
                print(service.statistics())
            elif choice == "12":
                inspect_object(service.find_task(read_int("ID задачи: ")))
            elif choice == "13":
                print(service.statistics_in_context())
            elif choice == "0":
                break
            else:
                print("Нет такого пункта")
        except (ValueError, EntityNotFoundError, InvalidStatusError) as error:
            print("Ошибка:", error)


if __name__ == "__main__":
    main()
