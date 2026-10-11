from datetime import date
from typing import Protocol

class BadStorage(Protocol):
    def add(self, item): ...
    def get(self, item_id): ...
    def delete(self, item_id): ...
    def save_to_file(self): ...
    def send_notification(self): ...
    def calculate_priority(self): ...

class BadProject:
    def __init__(self, project_id: int, name: str) -> None:
        self.id = project_id
        self.name = name

class UrgentTask(BadProject):
    def __init__(self, task_id: int, title: str, deadline: date) -> None:
        super().__init__(task_id, title)
        self.deadline = deadline

class BadMemoryStorage:
    def __init__(self) -> None:
        self.items = {}

    def add(self, item) -> None:
        self.items[item.id] = item

    def get(self, item_id: int):
        return self.items.get(item_id)

    def delete(self, item_id: int) -> None:
        self.items.pop(item_id, None)

    def save_to_file(self) -> None:
        pass

    def send_notification(self) -> None:
        pass

    def calculate_priority(self) -> int:
        return 0

class BadTaskManager:
    def __init__(self) -> None:
        self.storage: BadStorage = BadMemoryStorage()
        self.projects = {}
        self.tasks = {}

    def create_project(self, project_id: int, name: str) -> None:
        project = BadProject(project_id, name)
        self.projects[project_id] = project
        self.storage.add(project)
        print("Проект создан")

    def create_task(
        self,
        task_id: int,
        title: str,
        deadline: date,
        priority_mode: str,
        complexity: int,
    ) -> None:
        task = UrgentTask(task_id, title, deadline)
        if priority_mode == "deadline":
            priority = max(1, 10 - (deadline - date.today()).days)
        elif priority_mode == "complexity":
            priority = complexity
        else:
            priority = 1
        task.priority = priority
        self.tasks[task_id] = task
        self.storage.add(task)
        print(f"Задача создана, приоритет: {priority}")

if __name__ == "__main__":
    manager = BadTaskManager()
    manager.create_project(1, "Учебный проект")
    manager.create_task(2, "Подготовить отчёт", date.today(), "deadline", 5)