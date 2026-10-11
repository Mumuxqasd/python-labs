from datetime import date, timedelta
from models import TaskStatus
from priority import ComplexityPriorityStrategy, DeadlinePriorityStrategy, ManualPriorityStrategy
from repository import InMemoryRepository
from service import TaskService

def make_service():
    return TaskService(InMemoryRepository(), ManualPriorityStrategy())

def test_create_project():
    service = make_service()
    project = service.create_project("Проект")
    assert project.name == "Проект"

def test_create_task():
    service = make_service()
    project = service.create_project("Проект")
    task = service.create_task(project.id, "Задача", date.today(), 4, 3)
    assert task.project_id == project.id

def test_assign_executor():
    service = make_service()
    project = service.create_project("Проект")
    task = service.create_task(project.id, "Задача", date.today(), 4, 3)
    service.assign_executor(task.id, "Иван")
    assert task.assignee == "Иван"

def test_change_status():
    service = make_service()
    project = service.create_project("Проект")
    task = service.create_task(project.id, "Задача", date.today(), 4, 3)
    service.change_status(task.id, TaskStatus.COMPLETED)
    assert task.status == TaskStatus.COMPLETED

def test_strategies_are_replaceable():
    service = make_service()
    project = service.create_project("Проект")
    service.create_task(project.id, "Задача", date.today() + timedelta(days=1), 8, 2)
    service.set_priority_strategy(ComplexityPriorityStrategy())
    complexity_value = service.report()[0][1]
    service.set_priority_strategy(DeadlinePriorityStrategy())
    deadline_value = service.report()[0][1]
    assert complexity_value == 8
    assert deadline_value == 9