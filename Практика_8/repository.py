from typing import Protocol

from models import Task


class TaskRepository(Protocol):
    def add(self, task: Task) -> None: ...
    def get(self, task_id: int) -> Task | None: ...
    def get_all(self) -> list[Task]: ...
    def delete(self, task_id: int) -> None: ...


class InMemoryTaskRepository:
    def __init__(self) -> None:
        self.tasks: dict[int, Task] = {}

    def add(self, task: Task) -> None:
        self.tasks[task.id] = task

    def get(self, task_id: int) -> Task | None:
        return self.tasks.get(task_id)

    def get_all(self) -> list[Task]:
        return list(self.tasks.values())

    def delete(self, task_id: int) -> None:
        self.tasks.pop(task_id, None)
