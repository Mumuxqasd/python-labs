from datetime import date, timedelta

from models import TaskStatus
from priority import ComplexityPriorityStrategy, DeadlinePriorityStrategy, ManualPriorityStrategy
from repository import InMemoryRepository
from service import TaskService


def print_report(service: TaskService, title: str) -> None:
    print(f"\n=== {title} ===")
    for task, priority in service.report():
        print(
            f"{task.id}. {task.name}; статус: {task.status.value}; "
            f"исполнитель: {task.assignee or 'не назначен'}; приоритет: {priority}"
        )


def main() -> None:
    repository = InMemoryRepository()
    service = TaskService(repository, ManualPriorityStrategy())

    print("=== ДЕМОНСТРАЦИЯ ЛАБОРАТОРНОЙ РАБОТЫ №7 ===")

    project = service.create_project("Учебный проект", "Подготовка лабораторных работ")
    task1 = service.create_task(
        project.id,
        "Подготовить отчёт",
        date.today() + timedelta(days=2),
        6,
        8,
    )
    task2 = service.create_task(
        project.id,
        "Проверить программу",
        date.today() + timedelta(days=7),
        9,
        3,
    )

    service.assign_executor(task1.id, "Иван")
    service.assign_executor(task2.id, "Анна")
    service.change_status(task1.id, TaskStatus.IN_PROGRESS)

    print(f"Проект: {project.id} - {project.name}")
    print(f"Создано задач: {len(service.get_tasks())}")
    print(f"Repository: {type(repository).__name__}")

    print_report(service, "РУЧНОЙ ПРИОРИТЕТ")

    service.set_priority_strategy(ComplexityPriorityStrategy())
    print_report(service, "ПРИОРИТЕТ ПО СЛОЖНОСТИ")

    service.set_priority_strategy(DeadlinePriorityStrategy())
    print_report(service, "ПРИОРИТЕТ ПО СРОКУ")

    print("\nСтратегии успешно заменяются без изменения TaskService.")
    print("Демонстрация завершена успешно.")


if __name__ == "__main__":
    main()
