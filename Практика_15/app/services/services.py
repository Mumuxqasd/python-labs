from ..repositories.repositories import SmartHomeRepository


class SmartHomeService:
    statuses = {"online", "offline"}

    def __init__(self, repository: SmartHomeRepository) -> None:
        self.repository = repository

    def create_user(self, name: str, email: str):
        if not name.strip() or "@" not in email:
            raise ValueError("Некорректные данные пользователя")
        return self.repository.create_user(name.strip(), email.strip())

    def create_device(self, user_id: int, name: str, device_type: str, room: str, status: str):
        if status not in self.statuses:
            raise ValueError("Статус должен быть online или offline")
        if not name.strip() or not device_type.strip() or not room.strip():
            raise ValueError("Поля не должны быть пустыми")
        return self.repository.create_device(user_id, name.strip(), device_type.strip(), room.strip(), status)

    def list_devices(self, search: str | None = None, status: str | None = None, sort: str = "name"):
        return self.repository.list_devices(search, status, sort)

    def get_device(self, device_id: int):
        device = self.repository.get_device(device_id)
        if device is None:
            raise ValueError("Устройство не найдено")
        return device

    def update_device(self, device_id: int, name: str, room: str, status: str):
        device = self.get_device(device_id)
        if status not in self.statuses:
            raise ValueError("Некорректный статус")
        device.name = name.strip()
        device.room = room.strip()
        device.status = status
        return self.repository.update_device(device)

    def delete_device(self, device_id: int) -> None:
        self.repository.delete_device(self.get_device(device_id))

    def add_measurement(self, device_id: int, value: float):
        self.get_device(device_id)
        if value < -1000 or value > 1000:
            raise ValueError("Некорректное показание")
        return self.repository.add_measurement(device_id, value)
