from dataclasses import dataclass
from datetime import date


@dataclass
class SimpleTask:
    id: int
    title: str
    task_type: str
    priority: int
    complexity: int
    deadline: date
    completed: bool = False


class NaiveTaskManager:
    def __init__(self) -> None:
        self.tasks: list[SimpleTask] = []

    def create_task(self, task_type: str, task_id: int, title: str, priority: int, complexity: int, deadline: date) -> None:
        if task_type == "normal":
            task = SimpleTask(task_id, title, "normal", priority, complexity, deadline)
        elif task_type == "urgent":
            task = SimpleTask(task_id, title, "urgent", priority + 3, complexity, deadline)
        elif task_type == "recurring":
            task = SimpleTask(task_id, title, "recurring", priority, complexity, deadline)
        else:
            raise ValueError("Неизвестный тип задачи")
        self.tasks.append(task)

    def sort_tasks(self, mode: str) -> list[SimpleTask]:
        if mode == "deadline":
            return sorted(self.tasks, key=lambda task: task.deadline)
        if mode == "priority":
            return sorted(self.tasks, key=lambda task: task.priority, reverse=True)
        if mode == "complexity":
            return sorted(self.tasks, key=lambda task: task.complexity, reverse=True)
        return self.tasks

    def execute(self, command: str, task_id: int) -> None:
        if command == "delete":
            self.tasks = [task for task in self.tasks if task.id != task_id]
        elif command == "complete":
            for task in self.tasks:
                if task.id == task_id:
                    task.completed = True


if __name__ == "__main__":
    manager = NaiveTaskManager()
    manager.create_task("urgent", 1, "Сдать отчёт", 5, 4, date.today())
    print(manager.sort_tasks("priority"))
