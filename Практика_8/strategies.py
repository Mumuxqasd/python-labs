from typing import Protocol

from models import Task


class SortStrategy(Protocol):
    def sort(self, tasks: list[Task]) -> list[Task]: ...


class DeadlineSortStrategy:
    def sort(self, tasks: list[Task]) -> list[Task]:
        return sorted(tasks, key=lambda task: task.deadline)


class PrioritySortStrategy:
    def sort(self, tasks: list[Task]) -> list[Task]:
        return sorted(tasks, key=lambda task: task.priority, reverse=True)


class ComplexitySortStrategy:
    def sort(self, tasks: list[Task]) -> list[Task]:
        return sorted(tasks, key=lambda task: task.complexity, reverse=True)
