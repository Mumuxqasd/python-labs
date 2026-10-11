from models import Entity

class InMemoryRepository:
    def __init__(self) -> None:
        self.items: dict[int, Entity] = {}

    def add(self, entity: Entity) -> None:
        self.items[entity.id] = entity

    def update(self, entity: Entity) -> None:
        self.items[entity.id] = entity

    def delete(self, entity_id: int) -> None:
        self.items.pop(entity_id, None)

    def get(self, entity_id: int) -> Entity | None:
        return self.items.get(entity_id)

    def get_all(self) -> list[Entity]:
        return list(self.items.values())