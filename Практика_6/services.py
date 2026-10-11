from datetime import date
from inspect import signature

from context import OperationContext
from decorators import action, log_call, measure_time
from exceptions import EntityNotFoundError, InvalidStatusError
from models import Entity, Project, Task, TaskStatus, User


class TaskService:
    def __init__(self) -> None:
        self.users: list[User] = []
        self.projects: list[Project] = []
        self.tasks: list[Task] = []
        self.next_user_id = 1
        self.next_project_id = 1
        self.next_task_id = 1

    @log_call
    def add_user(self, name: str) -> User:
        if not name.strip():
            raise ValueError("Имя пользователя не может быть пустым")
        user = User(self.next_user_id, name.strip())
        self.next_user_id += 1
        self.users.append(user)
        return user

    @log_call
    def add_project(self, name: str) -> Project:
        if not name.strip():
            raise ValueError("Название проекта не может быть пустым")
        project = Project(self.next_project_id, name.strip())
        self.next_project_id += 1
        self.projects.append(project)
        return project

    @log_call
    def add_task(self, name: str, project_id: int, deadline: date) -> Task:
        project = self.find_project(project_id)
        if not name.strip():
            raise ValueError("Название задачи не может быть пустым")
        task = Task(self.next_task_id, name.strip(), project_id, deadline)
        self.next_task_id += 1
        self.tasks.append(task)
        project.task_ids.append(task.id)
        return task

    def delete_task(self, task_id: int) -> None:
        task = self.find_task(task_id)
        self.tasks.remove(task)
        project = self.find_project(task.project_id)
        if task.id in project.task_ids:
            project.task_ids.remove(task.id)
        if task.assignee_id is not None:
            user = self.find_user(task.assignee_id)
            if task.id in user.assigned_task_ids:
                user.assigned_task_ids.remove(task.id)

    def find_task(self, task_id: int) -> Task:
        for task in self.tasks:
            if task.id == task_id:
                return task
        raise EntityNotFoundError("Задача не найдена")

    def find_project(self, project_id: int) -> Project:
        for project in self.projects:
            if project.id == project_id:
                return project
        raise EntityNotFoundError("Проект не найден")

    def find_user(self, user_id: int) -> User:
        for user in self.users:
            if user.id == user_id:
                return user
        raise EntityNotFoundError("Пользователь не найден")

    @action("Назначение задачи пользователю")
    def assign_task(self, task_id: int, user_id: int) -> None:
        task = self.find_task(task_id)
        user = self.find_user(user_id)
        if task.assignee_id is not None and task.assignee_id != user_id:
            old_user = self.find_user(task.assignee_id)
            if task.id in old_user.assigned_task_ids:
                old_user.assigned_task_ids.remove(task.id)
        task.assignee_id = user_id
        if task.id not in user.assigned_task_ids:
            user.assigned_task_ids.append(task.id)

    def change_status(self, task_id: int, new_status: TaskStatus) -> None:
        task = self.find_task(task_id)
        allowed = {
            TaskStatus.NEW: {TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED},
            TaskStatus.IN_PROGRESS: {TaskStatus.COMPLETED, TaskStatus.CANCELLED},
            TaskStatus.COMPLETED: set(),
            TaskStatus.CANCELLED: set(),
        }
        if new_status not in allowed[task.status]:
            raise InvalidStatusError(
                f"Нельзя изменить статус {task.status.value} на {new_status.value}"
            )
        task.status = new_status

    def overdue_tasks(self) -> list[Task]:
        today = date.today()
        return [
            task
            for task in self.tasks
            if task.deadline < today
            and task.status not in {TaskStatus.COMPLETED, TaskStatus.CANCELLED}
        ]

    def user_load(self) -> list[tuple[User, int]]:
        result: list[tuple[User, int]] = []
        for user in self.users:
            active = 0
            for task_id in user.assigned_task_ids:
                task = self.find_task(task_id)
                if task.status in {TaskStatus.NEW, TaskStatus.IN_PROGRESS}:
                    active += 1
            result.append((user, active))
        return result

    @log_call
    @measure_time
    def statistics(self) -> dict[str, int]:
        return {
            "projects": len(self.projects),
            "users": len(self.users),
            "tasks": len(self.tasks),
            "new": sum(task.status == TaskStatus.NEW for task in self.tasks),
            "in_progress": sum(
                task.status == TaskStatus.IN_PROGRESS for task in self.tasks
            ),
            "completed": sum(
                task.status == TaskStatus.COMPLETED for task in self.tasks
            ),
            "cancelled": sum(
                task.status == TaskStatus.CANCELLED for task in self.tasks
            ),
            "overdue": len(self.overdue_tasks()),
        }

    def statistics_in_context(self) -> dict[str, int]:
        with OperationContext("формирование статистики"):
            return self.statistics()


def inspect_object(obj: Entity) -> None:
    print("=== ИНФОРМАЦИЯ ОБ ОБЪЕКТЕ ===")
    print("Тип:", type(obj).__name__)
    print("Entity:", isinstance(obj, Entity))
    print("Класс-наследник Entity:", issubclass(obj.__class__, Entity))
    print("Есть name:", hasattr(obj, "name"))
    if hasattr(obj, "name"):
        print("name:", getattr(obj, "name"))
    attributes = [name for name in dir(obj) if not name.startswith("_")]
    print("Атрибуты и методы:", ", ".join(attributes))
    print("Сигнатура get_report_data:", signature(obj.get_report_data))
