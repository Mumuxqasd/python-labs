from dataclasses import dataclass, field
from datetime import date
from enum import Enum

class TaskStatus(Enum):
    NEW = "новая"
    IN_PROGRESS = "выполняется"
    COMPLETED = "завершена"
    CANCELLED = "отменена"

@dataclass
class Entity:
    id: int
    name: str

    def get_report_data(self) -> str:
        return f"{self.id}: {self.name}"

@dataclass
class User(Entity):
    assigned_task_ids: list[int] = field(default_factory=list)

    def get_report_data(self) -> str:
        return f"Пользователь {self.id}: {self.name}, задач: {len(self.assigned_task_ids)}"

@dataclass
class Project(Entity):
    task_ids: list[int] = field(default_factory=list)

    def get_report_data(self) -> str:
        return f"Проект {self.id}: {self.name}, задач: {len(self.task_ids)}"

@dataclass
class Task(Entity):
    project_id: int
    deadline: date
    status: TaskStatus = TaskStatus.NEW
    assignee_id: int | None = None

    def get_report_data(self) -> str:
        assignee = self.assignee_id if self.assignee_id is not None else "не назначен"
        return (
            f"Задача {self.id}: {self.name}, статус: {self.status.value}, "
            f"срок: {self.deadline}, исполнитель: {assignee}"
        )