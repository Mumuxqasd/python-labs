import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base
from exceptions import DuplicateError, NotFoundError, ValidationError
from repository import SmartHomeRepository
from service import SmartHomeService


@pytest.fixture
def service():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    session = Session()
    repo = SmartHomeRepository(session)
    yield SmartHomeService(repo), repo
    session.close()


def test_add_user(service):
    srv, repo = service
    assert srv.add_user("Ivan", "ivan@test.ru").id == 1


def test_duplicate_user(service):
    srv, repo = service
    srv.add_user("Ivan", "ivan@test.ru")
    with pytest.raises(DuplicateError):
        srv.add_user("Other", "ivan@test.ru")


def test_add_device(service):
    srv, repo = service
    user = srv.add_user("Ivan", "ivan@test.ru")
    assert srv.add_device(user.id, "Lamp", "L-1", "light").serial == "L-1"


def test_missing_user(service):
    srv, repo = service
    with pytest.raises(NotFoundError):
        srv.add_device(999, "Lamp", "L-1", "light")


def test_filter_and_sort(service):
    srv, repo = service
    user = srv.add_user("Ivan", "ivan@test.ru")
    srv.add_device(user.id, "B", "B-1", "light", "offline")
    srv.add_device(user.id, "A", "A-1", "sensor", "online")
    assert len(repo.filter_devices(status="online")) == 1
    assert repo.sort_devices("name")[0].name == "A"


def test_search(service):
    srv, repo = service
    user = srv.add_user("Ivan", "ivan@test.ru")
    srv.add_device(user.id, "Temperature", "TMP-1", "sensor")
    assert len(repo.search_devices("TMP")) == 1


def test_update(service):
    srv, repo = service
    user = srv.add_user("Ivan", "ivan@test.ru")
    device = srv.add_device(user.id, "Lamp", "L-1", "light")
    assert srv.change_device(device.id, status="online").status == "online"


def test_delete(service):
    srv, repo = service
    user = srv.add_user("Ivan", "ivan@test.ru")
    device = srv.add_device(user.id, "Lamp", "L-1", "light")
    srv.remove_device(device.id)
    with pytest.raises(NotFoundError):
        srv.get_device(device.id)


def test_transaction_measurement(service):
    srv, repo = service
    user = srv.add_user("Ivan", "ivan@test.ru")
    device = srv.add_device(user.id, "Sensor", "S-1", "temperature")
    srv.save_measurement(device.id, 25.0, "online")
    assert repo.get_device(device.id).last_value == 25.0
    assert len(repo.get_measurements(device.id)) == 1


def test_validation(service):
    srv, repo = service
    with pytest.raises(ValidationError):
        srv.add_user("", "bad")
