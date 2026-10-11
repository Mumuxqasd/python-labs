from datetime import date, timedelta
from exceptions import InvalidStatusError
from models import TaskStatus
from protocols import print_report_item
from services import TaskService, inspect_object

def main() -> None:
    service = TaskService()

    print("=== ДЕМОНСТРАЦИЯ ЛАБОРАТОРНОЙ РАБОТЫ №6 ===")

    user1 = service.add_user("Иван")
    user2 = service.add_user("Анна")
    project = service.add_project("Учебный проект")

    task1 = service.add_task(
        "Подготовить отчёт",
        project.id,
        date.today() - timedelta(days=3),
    )
    task2 = service.add_task(
        "Проверить программу",
        project.id,
        date.today() + timedelta(days=7),
    )
    task3 = service.add_task(
        "Сдать лабораторную",
        project.id,
        date.today() + timedelta(days=10),
    )

    service.assign_task(task1.id, user1.id)
    service.assign_task(task2.id, user2.id)
    service.assign_task(task3.id, user1.id)

    service.change_status(task1.id, TaskStatus.IN_PROGRESS)
    service.change_status(task3.id, TaskStatus.IN_PROGRESS)
    service.change_status(task3.id, TaskStatus.COMPLETED)

    print("\n=== ОБЪЕКТЫ ЧЕРЕЗ PROTOCOL ===")
    print_report_item(project)
    print_report_item(user1)
    print_report_item(user2)
    print_report_item(task1)
    print_report_item(task2)
    print_report_item(task3)

    print("\n=== ПРОСРОЧЕННЫЕ ЗАДАЧИ ===")
    for task in service.overdue_tasks():
        print_report_item(task)

    print("\n=== ЗАГРУЗКА ПОЛЬЗОВАТЕЛЕЙ ===")
    for user, load in service.user_load():
        print(f"{user.name}: {load} активных задач")

    print("\n=== СТАТИСТИКА И ДЕКОРАТОРЫ ===")
    print(service.statistics())
    print("Имя декорированной функции:", service.add_user.__name__)

    print("\n=== КОНТЕКСТНЫЙ МЕНЕДЖЕР ===")
    print(service.statistics_in_context())

    print("\n=== ИНТРОСПЕКЦИЯ ===")
    inspect_object(task1)

    print("\n=== ПРОВЕРКА ОШИБОЧНОГО ПЕРЕХОДА СТАТУСА ===")
    try:
        service.change_status(task3.id, TaskStatus.IN_PROGRESS)
    except InvalidStatusError as error:
        print("Ошибка обработана:", error)
        
    print("\nДемонстрация завершена успешно.")
    i = input()


if __name__ == "__main__":
    main()