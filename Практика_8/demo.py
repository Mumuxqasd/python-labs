from datetime import date, timedelta

from commands import CompleteTaskCommand, CreateTaskCommand, DeleteTaskCommand, UpdateTaskCommand
from repository import InMemoryTaskRepository
from service import TaskService
from strategies import ComplexitySortStrategy, DeadlineSortStrategy, PrioritySortStrategy


def print_tasks(service: TaskService, title: str) -> None:
    print(f"\n=== {title} ===")
    for task in service.get_sorted_tasks():
        print(
            f"{task.id}. {task.title}; тип: {task.kind}; статус: {task.status.value}; "
            f"приоритет: {task.priority}; сложность: {task.complexity}"
        )


def main() -> None:
    repository = InMemoryTaskRepository()
    service = TaskService(repository, DeadlineSortStrategy())

    print("=== ДЕМОНСТРАЦИЯ ЛАБОРАТОРНОЙ РАБОТЫ №8 ===")

    CreateTaskCommand(
        service, "normal", "Подготовить отчёт", date.today() + timedelta(days=5), 5, 4
    ).execute()
    CreateTaskCommand(
        service, "urgent", "Исправить ошибку", date.today() + timedelta(days=1), 9, 7
    ).execute()
    CreateTaskCommand(
        service, "recurring", "Проверить резервную копию", date.today() + timedelta(days=3), 4, 8
    ).execute()

    print_tasks(service, "СОРТИРОВКА ПО СРОКУ")

    service.set_sort_strategy(PrioritySortStrategy())
    print_tasks(service, "СОРТИРОВКА ПО ПРИОРИТЕТУ")

    service.set_sort_strategy(ComplexitySortStrategy())
    print_tasks(service, "СОРТИРОВКА ПО СЛОЖНОСТИ")

    UpdateTaskCommand(service, 1, "Подготовить итоговый отчёт").execute()
    CompleteTaskCommand(service, 2).execute()
    DeleteTaskCommand(service, 3).execute()

    print("\n=== РЕЗУЛЬТАТ COMMAND ===")
    for task in repository.get_all():
        print(f"{task.id}. {task.title}; {task.kind}; {task.status.value}")

    print("\nFactory создал разные типы задач, Repository сохранил их в памяти.")
    print("Демонстрация завершена успешно.")


if __name__ == "__main__":
    main()
