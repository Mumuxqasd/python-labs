from sqlalchemy import and_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from exceptions import DuplicateError, NotFoundError
from models import Device, Measurement, User


class SmartHomeRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_user(self, name: str, email: str) -> User:
        user = User(name=name, email=email)
        self.session.add(user)
        try:
            self.session.commit()
        except IntegrityError as error:
            self.session.rollback()
            raise DuplicateError("Пользователь с таким email уже существует") from error
        return user

    def get_user(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)

    def create_device(self, user_id: int, name: str, serial: str, device_type: str, status: str) -> Device:
        device = Device(user_id=user_id, name=name, serial=serial, device_type=device_type, status=status)
        self.session.add(device)
        try:
            self.session.commit()
        except IntegrityError as error:
            self.session.rollback()
            raise DuplicateError("Устройство с таким serial уже существует или пользователь не найден") from error
        return device

    def get_device(self, device_id: int) -> Device | None:
        return self.session.get(Device, device_id)

    def list_devices(self) -> list[Device]:
        return list(self.session.scalars(select(Device)).all())

    def filter_devices(self, status: str | None = None, user_id: int | None = None) -> list[Device]:
        statement = select(Device)
        conditions = []
        if status is not None:
            conditions.append(Device.status == status)
        if user_id is not None:
            conditions.append(Device.user_id == user_id)
        if conditions:
            statement = statement.where(and_(*conditions))
        return list(self.session.scalars(statement).all())

    def search_devices(self, text: str) -> list[Device]:
        pattern = f"%{text}%"
        statement = select(Device).where((Device.name.ilike(pattern)) | (Device.serial.ilike(pattern)))
        return list(self.session.scalars(statement).all())

    def sort_devices(self, field: str, desc: bool = False) -> list[Device]:
        columns = {"name": Device.name, "serial": Device.serial, "status": Device.status}
        column = columns.get(field, Device.name)
        statement = select(Device).order_by(column.desc() if desc else column.asc())
        return list(self.session.scalars(statement).all())

    def update_device(self, device_id: int, **changes) -> Device:
        device = self.session.get(Device, device_id)
        if device is None:
            raise NotFoundError("Устройство не найдено")
        for key, value in changes.items():
            if hasattr(device, key):
                setattr(device, key, value)
        try:
            self.session.commit()
        except IntegrityError as error:
            self.session.rollback()
            raise DuplicateError("Нарушено уникальное ограничение") from error
        return device

    def delete_device(self, device_id: int) -> None:
        device = self.session.get(Device, device_id)
        if device is None:
            raise NotFoundError("Устройство не найдено")
        self.session.delete(device)
        self.session.commit()

    def get_measurements(self, device_id: int) -> list[Measurement]:
        statement = select(Measurement).where(Measurement.device_id == device_id).order_by(Measurement.id)
        return list(self.session.scalars(statement).all())

    def register_measurement(self, device_id: int, value: float, status: str) -> Measurement:
        device = self.session.get(Device, device_id)
        if device is None:
            raise NotFoundError("Устройство не найдено")
        measurement = Measurement(device_id=device_id, value=value)
        device.last_value = value
        device.status = status
        self.session.add(measurement)
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
        return measurement
