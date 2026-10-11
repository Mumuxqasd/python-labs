from datetime import date
from typing import Protocol

from service import TaskService


class Command(Protocol):
    def execute(self) -> None: ...


class CreateTaskCommand:
    def __init__(
        self,
        service: TaskService,
        task_type: str,
        title: str,
        deadline: date,
        priority: int,
        complexity: int,
    ) -> None:
        self.service = service
        self.task_type = task_type
        self.title = title
        self.deadline = deadline
        self.priority = priority
        self.complexity = complexity

    def execute(self) -> None:
        task = self.service.create_task(
            self.task_type,
            self.title,
            self.deadline,
            self.priority,
            self.complexity,
        )
        print("Создана задача:", task.id)


class DeleteTaskCommand:
    def __init__(self, service: TaskService, task_id: int) -> None:
        self.service = service
        self.task_id = task_id

    def execute(self) -> None:
        self.service.delete_task(self.task_id)


class UpdateTaskCommand:
    def __init__(self, service: TaskService, task_id: int, title: str) -> None:
        self.service = service
        self.task_id = task_id
        self.title = title

    def execute(self) -> None:
        self.service.update_task(self.task_id, self.title)


class CompleteTaskCommand:
    def __init__(self, service: TaskService, task_id: int) -> None:
        self.service = service
        self.task_id = task_id

    def execute(self) -> None:
        self.service.complete_task(self.task_id)
