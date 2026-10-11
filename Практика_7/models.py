from dataclasses import dataclass, field
from datetime import date
from enum import Enum

class TaskStatus(Enum):
    NEW = "новая"
    IN_PROGRESS = "выполняется"
    COMPLETED = "завершена"

@dataclass
class Entity:
    id: int
    name: str

@dataclass
class Project(Entity):
    description: str = ""

@dataclass
class Task(Entity):
    project_id: int = 0
    deadline: date = field(default_factory=date.today)
    complexity: int = 1
    manual_priority: int = 1
    assignee: str = ""
    status: TaskStatus = TaskStatus.NEW
