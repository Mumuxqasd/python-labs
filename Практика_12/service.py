from exceptions import NotFoundError, ValidationError
from repository import SmartHomeRepository


class SmartHomeService:
    statuses = {"online", "offline"}

    def __init__(self, repository: SmartHomeRepository) -> None:
        self.repository = repository

    def add_user(self, name: str, email: str):
        if not name.strip() or "@" not in email:
            raise ValidationError("Некорректные данные пользователя")
        return self.repository.create_user(name.strip(), email.strip())

    def add_device(self, user_id: int, name: str, serial: str, device_type: str, status: str = "offline"):
        if self.repository.get_user(user_id) is None:
            raise NotFoundError("Пользователь не найден")
        if not name.strip() or not serial.strip() or not device_type.strip():
            raise ValidationError("Поля устройства не должны быть пустыми")
        if status not in self.statuses:
            raise ValidationError("Статус должен быть online или offline")
        return self.repository.create_device(user_id, name.strip(), serial.strip(), device_type.strip(), status)

    def get_device(self, device_id: int):
        device = self.repository.get_device(device_id)
        if device is None:
            raise NotFoundError("Устройство не найдено")
        return device

    def change_device(self, device_id: int, **changes):
        if "status" in changes and changes["status"] not in self.statuses:
            raise ValidationError("Некорректный статус")
        return self.repository.update_device(device_id, **changes)

    def remove_device(self, device_id: int) -> None:
        self.repository.delete_device(device_id)

    def save_measurement(self, device_id: int, value: float, status: str = "online"):
        if status not in self.statuses:
            raise ValidationError("Некорректный статус")
        if value < -1000 or value > 1000:
            raise ValidationError("Некорректное показание")
        return self.repository.register_measurement(device_id, value, status)
