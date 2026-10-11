from datetime import date

from models import NormalTask, RecurringTask, Task, UrgentTask


class TaskFactory:
    @staticmethod
    def create(
        task_type: str,
        task_id: int,
        title: str,
        deadline: date,
        priority: int,
        complexity: int,
    ) -> Task:
        if task_type == "normal":
            return NormalTask(task_id, title, deadline, priority, complexity)
        if task_type == "urgent":
            return UrgentTask(task_id, title, deadline, priority, complexity)
        if task_type == "recurring":
            return RecurringTask(task_id, title, deadline, priority, complexity)
        raise ValueError("Неизвестный тип задачи")
