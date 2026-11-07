import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.repositories.repositories import SmartHomeRepository
from app.services.services import SmartHomeService


@pytest.fixture
def service():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    session = Session()
    yield SmartHomeService(SmartHomeRepository(session))
    session.close()


def user_and_device(service):
    user = service.create_user("Ivan", "ivan@example.com")
    device = service.create_device(user.id, "Lamp", "light", "Room", "offline")
    return user, device


def test_user(service):
    assert service.create_user("Ivan", "ivan@example.com").id == 1


def test_device_create(service):
    user = service.create_user("Ivan", "ivan@example.com")
    assert service.create_device(user.id, "Lamp", "light", "Room", "offline").id == 1


def test_list(service):
    user_and_device(service)
    assert len(service.list_devices()) == 1


def test_search(service):
    user_and_device(service)
    assert len(service.list_devices(search="Lamp")) == 1


def test_filter(service):
    user_and_device(service)
    assert len(service.list_devices(status="offline")) == 1


def test_update(service):
    user, device = user_and_device(service)
    assert service.update_device(device.id, "New", "Room2", "online").status == "online"


def test_measurement(service):
    user, device = user_and_device(service)
    service.add_measurement(device.id, 10.5)
    assert service.repository.measurements(device.id)[0].value == 10.5


def test_delete(service):
    user, device = user_and_device(service)
    service.delete_device(device.id)
    assert service.list_devices() == []
