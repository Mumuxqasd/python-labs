from datetime import date
from models import Task

class ManualPriorityStrategy:
    def calculate(self, task: Task) -> int:
        return task.manual_priority

class ComplexityPriorityStrategy:
    def calculate(self, task: Task) -> int:
        return task.complexity

class DeadlinePriorityStrategy:
    def calculate(self, task: Task) -> int:
        days = (task.deadline - date.today()).days
        if days <= 0:
            return 10
        if days >= 9:
            return 1
        return 10 - days