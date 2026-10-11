from datetime import date
from models import TaskStatus
from priority import ComplexityPriorityStrategy, DeadlinePriorityStrategy, ManualPriorityStrategy
from service import TaskService

class ConsoleUI:
    def __init__(self, service: TaskService) -> None:
        self.service = service

    def run(self) -> None:
        while True:
            print("\n=== МЕНЕДЖЕР ЗАДАЧ ===")
            print("1. Создать проект")
            print("2. Создать задачу")
            print("3. Назначить исполнителя")
            print("4. Изменить статус")
            print("5. Выбрать стратегию приоритета")
            print("6. Сформировать отчёт")
            print("0. Выход")
            choice = input("Выберите пункт: ").strip()
            try:
                if choice == "1":
                    project = self.service.create_project(
                        input("Название: "), input("Описание: ")
                    )
                    print("Создан проект:", project)
                elif choice == "2":
                    task = self.service.create_task(
                        int(input("ID проекта: ")),
                        input("Название: "),
                        date.fromisoformat(input("Срок ГГГГ-ММ-ДД: ")),
                        int(input("Сложность 1-10: ")),
                        int(input("Ручной приоритет 1-10: ")),
                    )
                    print("Создана задача:", task)
                elif choice == "3":
                    self.service.assign_executor(
                        int(input("ID задачи: ")), input("Исполнитель: ")
                    )
                elif choice == "4":
                    task_id = int(input("ID задачи: "))
                    print("1. новая  2. выполняется  3. завершена")
                    number = int(input("Статус: "))
                    status = list(TaskStatus)[number - 1]
                    self.service.change_status(task_id, status)
                elif choice == "5":
                    print("1. Ручной  2. По сложности  3. По сроку")
                    number = input("Стратегия: ").strip()
                    strategies = {
                        "1": ManualPriorityStrategy(),
                        "2": ComplexityPriorityStrategy(),
                        "3": DeadlinePriorityStrategy(),
                    }
                    if number not in strategies:
                        raise ValueError("Нет такой стратегии")
                    self.service.set_priority_strategy(strategies[number])
                elif choice == "6":
                    for task, priority in self.service.report():
                        print(
                            f"{task.id}. {task.name}; {task.status.value}; "
                            f"исполнитель: {task.assignee or 'не назначен'}; приоритет: {priority}"
                        )
                elif choice == "0":
                    break
                else:
                    print("Нет такого пункта")
            except (ValueError, IndexError) as error:
                print("Ошибка:", error)
