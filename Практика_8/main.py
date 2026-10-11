from datetime import date

from commands import CompleteTaskCommand, CreateTaskCommand, DeleteTaskCommand, UpdateTaskCommand
from repository import InMemoryTaskRepository
from service import TaskService
from strategies import ComplexitySortStrategy, DeadlineSortStrategy, PrioritySortStrategy


def main() -> None:
    service = TaskService(InMemoryTaskRepository(), DeadlineSortStrategy())

    while True:
        print("\n=== МЕНЕДЖЕР ЗАДАЧ ===")
        print("1. Создать задачу")
        print("2. Удалить задачу")
        print("3. Изменить задачу")
        print("4. Завершить задачу")
        print("5. Выбрать сортировку")
        print("6. Показать задачи")
        print("0. Выход")
        choice = input("Выберите пункт: ").strip()
        try:
            if choice == "1":
                print("Тип: normal / urgent / recurring")
                command = CreateTaskCommand(
                    service,
                    input("Тип: ").strip(),
                    input("Название: "),
                    date.fromisoformat(input("Срок ГГГГ-ММ-ДД: ")),
                    int(input("Приоритет 1-10: ")),
                    int(input("Сложность 1-10: ")),
                )
                command.execute()
            elif choice == "2":
                DeleteTaskCommand(service, int(input("ID: "))).execute()
            elif choice == "3":
                UpdateTaskCommand(
                    service, int(input("ID: ")), input("Новое название: ")
                ).execute()
            elif choice == "4":
                CompleteTaskCommand(service, int(input("ID: "))).execute()
            elif choice == "5":
                print("1. По сроку  2. По приоритету  3. По сложности")
                number = input("Сортировка: ").strip()
                strategies = {
                    "1": DeadlineSortStrategy(),
                    "2": PrioritySortStrategy(),
                    "3": ComplexitySortStrategy(),
                }
                if number not in strategies:
                    raise ValueError("Нет такой стратегии")
                service.set_sort_strategy(strategies[number])
            elif choice == "6":
                for task in service.get_sorted_tasks():
                    print(
                        f"{task.id}. {task.title}; тип: {task.kind}; "
                        f"статус: {task.status.value}; срок: {task.deadline}; "
                        f"приоритет: {task.priority}; сложность: {task.complexity}"
                    )
            elif choice == "0":
                break
            else:
                print("Нет такого пункта")
        except (ValueError, IndexError) as error:
            print("Ошибка:", error)


if __name__ == "__main__":
    main()
