from datetime import date, timedelta

from commands import CompleteTaskCommand
from factory import TaskFactory
from models import TaskStatus, UrgentTask
from repository import InMemoryTaskRepository
from service import TaskService
from strategies import DeadlineSortStrategy, PrioritySortStrategy


def make_service():
    return TaskService(InMemoryTaskRepository(), DeadlineSortStrategy())


def test_factory_creates_urgent_task():
    task = TaskFactory.create("urgent", 1, "Срочно", date.today(), 8, 5)
    assert isinstance(task, UrgentTask)


def test_repository_add_and_get():
    repository = InMemoryTaskRepository()
    task = TaskFactory.create("normal", 1, "Задача", date.today(), 5, 5)
    repository.add(task)
    assert repository.get(1) is task


def test_priority_strategy():
    service = make_service()
    service.create_task("normal", "A", date.today(), 2, 5)
    service.create_task("normal", "B", date.today(), 9, 2)
    service.set_sort_strategy(PrioritySortStrategy())
    assert service.get_sorted_tasks()[0].title == "B"


def test_business_operation_update():
    service = make_service()
    task = service.create_task("normal", "Старое", date.today(), 3, 3)
    service.update_task(task.id, "Новое")
    assert task.title == "Новое"


def test_command_complete():
    service = make_service()
    task = service.create_task("normal", "Задача", date.today() + timedelta(days=1), 3, 3)
    CompleteTaskCommand(service, task.id).execute()
    assert task.status == TaskStatus.COMPLETED
