from typing import Protocol
from models import Entity, Task

class ReadRepository(Protocol):
    def get(self, entity_id: int) -> Entity | None:
        ...
    def get_all(self) -> list[Entity]:
        ...

class WriteRepository(Protocol):
    def add(self, entity: Entity) -> None:
        ...
    def update(self, entity: Entity) -> None:
        ...
    def delete(self, entity_id: int) -> None:
        ...

class Repository(ReadRepository, WriteRepository, Protocol):
    pass

class PriorityStrategy(Protocol):
    def calculate(self, task: Task) -> int:
        ...