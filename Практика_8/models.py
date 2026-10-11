from dataclasses import dataclass
from datetime import date
from enum import Enum


class TaskStatus(Enum):
    NEW = "новая"
    COMPLETED = "завершена"


@dataclass
class Task:
    id: int
    title: str
    deadline: date
    priority: int
    complexity: int
    status: TaskStatus = TaskStatus.NEW

    @property
    def kind(self) -> str:
        return "обычная"


@dataclass
class NormalTask(Task):
    pass


@dataclass
class UrgentTask(Task):
    @property
    def kind(self) -> str:
        return "срочная"


@dataclass
class RecurringTask(Task):
    interval_days: int = 7

    @property
    def kind(self) -> str:
        return "повторяющаяся"
