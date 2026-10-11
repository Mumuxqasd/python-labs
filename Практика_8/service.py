from datetime import date

from factory import TaskFactory
from models import Task, TaskStatus
from repository import TaskRepository
from strategies import SortStrategy


class TaskService:
    def __init__(self, repository: TaskRepository, sort_strategy: SortStrategy) -> None:
        self.repository = repository
        self.sort_strategy = sort_strategy
        self.next_id = 1

    def set_sort_strategy(self, strategy: SortStrategy) -> None:
        self.sort_strategy = strategy

    def create_task(
        self,
        task_type: str,
        title: str,
        deadline: date,
        priority: int,
        complexity: int,
    ) -> Task:
        if not title.strip():
            raise ValueError("Название не может быть пустым")
        if not 1 <= priority <= 10 or not 1 <= complexity <= 10:
            raise ValueError("Приоритет и сложность должны быть от 1 до 10")
        task = TaskFactory.create(
            task_type,
            self.next_id,
            title.strip(),
            deadline,
            priority,
            complexity,
        )
        self.next_id += 1
        self.repository.add(task)
        return task

    def delete_task(self, task_id: int) -> None:
        self._get_task(task_id)
        self.repository.delete(task_id)

    def update_task(self, task_id: int, title: str) -> None:
        task = self._get_task(task_id)
        if not title.strip():
            raise ValueError("Название не может быть пустым")
        task.title = title.strip()

    def complete_task(self, task_id: int) -> None:
        task = self._get_task(task_id)
        task.status = TaskStatus.COMPLETED

    def get_sorted_tasks(self) -> list[Task]:
        return self.sort_strategy.sort(self.repository.get_all())

    def _get_task(self, task_id: int) -> Task:
        task = self.repository.get(task_id)
        if task is None:
            raise ValueError("Задача не найдена")
        return task
