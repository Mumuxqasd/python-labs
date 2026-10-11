from datetime import date
from interfaces import PriorityStrategy, Repository
from models import Project, Task, TaskStatus

class TaskService:
    def __init__(self, repository: Repository, priority_strategy: PriorityStrategy) -> None:
        self.repository = repository
        self.priority_strategy = priority_strategy
        self.next_id = 1

    def set_priority_strategy(self, strategy: PriorityStrategy) -> None:
        self.priority_strategy = strategy

    def create_project(self, name: str, description: str = "") -> Project:
        if not name.strip():
            raise ValueError("Название проекта не может быть пустым")
        project = Project(self.next_id, name.strip(), description.strip())
        self.next_id += 1
        self.repository.add(project)
        return project

    def create_task(
        self,
        project_id: int,
        name: str,
        deadline: date,
        complexity: int,
        manual_priority: int,
    ) -> Task:
        project = self.repository.get(project_id)
        if not isinstance(project, Project):
            raise ValueError("Проект не найден")
        if not name.strip():
            raise ValueError("Название задачи не может быть пустым")
        if not 1 <= complexity <= 10:
            raise ValueError("Сложность должна быть от 1 до 10")
        if not 1 <= manual_priority <= 10:
            raise ValueError("Приоритет должен быть от 1 до 10")
        task = Task(
            self.next_id,
            name.strip(),
            project_id,
            deadline,
            complexity,
            manual_priority,
        )
        self.next_id += 1
        self.repository.add(task)
        return task

    def assign_executor(self, task_id: int, executor: str) -> None:
        task = self._get_task(task_id)
        if not executor.strip():
            raise ValueError("Исполнитель не может быть пустым")
        task.assignee = executor.strip()
        self.repository.update(task)

    def change_status(self, task_id: int, status: TaskStatus) -> None:
        task = self._get_task(task_id)
        task.status = status
        self.repository.update(task)

    def get_tasks(self) -> list[Task]:
        return [item for item in self.repository.get_all() if isinstance(item, Task)]

    def report(self) -> list[tuple[Task, int]]:
        result = [(task, self.priority_strategy.calculate(task)) for task in self.get_tasks()]
        return sorted(result, key=lambda item: item[1], reverse=True)

    def _get_task(self, task_id: int) -> Task:
        task = self.repository.get(task_id)
        if not isinstance(task, Task):
            raise ValueError("Задача не найдена")
        return task