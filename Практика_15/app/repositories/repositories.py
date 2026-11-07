from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from ..models.models import Device, Measurement, User


class SmartHomeRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_user(self, name: str, email: str) -> User:
        user = User(name=name, email=email)
        self.session.add(user)
        self.session.commit()
        return user

    def create_device(self, user_id: int, name: str, device_type: str, room: str, status: str) -> Device:
        device = Device(user_id=user_id, name=name, device_type=device_type, room=room, status=status)
        self.session.add(device)
        self.session.commit()
        return device

    def list_devices(self, search: str | None = None, status: str | None = None, sort: str = "name") -> list[Device]:
        statement = select(Device)
        if search:
            pattern = f"%{search}%"
            statement = statement.where(or_(Device.name.ilike(pattern), Device.room.ilike(pattern)))
        if status:
            statement = statement.where(Device.status == status)
        columns = {"name": Device.name, "room": Device.room, "status": Device.status}
        statement = statement.order_by(columns.get(sort, Device.name).asc())
        return list(self.session.scalars(statement).all())

    def get_device(self, device_id: int) -> Device | None:
        return self.session.get(Device, device_id)

    def update_device(self, device: Device) -> Device:
        self.session.commit()
        return device

    def delete_device(self, device: Device) -> None:
        self.session.delete(device)
        self.session.commit()

    def add_measurement(self, device_id: int, value: float) -> Measurement:
        measurement = Measurement(device_id=device_id, value=value)
        self.session.add(measurement)
        self.session.commit()
        return measurement

    def measurements(self, device_id: int) -> list[Measurement]:
        return list(self.session.scalars(select(Measurement).where(Measurement.device_id == device_id).order_by(Measurement.id)).all())
