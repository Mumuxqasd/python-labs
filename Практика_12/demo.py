from sqlalchemy.pool import StaticPool

from database import Base, make_engine, make_session_factory
from repository import SmartHomeRepository
from service import SmartHomeService


def main() -> None:
    print("=== ДЕМОНСТРАЦИЯ ЛАБОРАТОРНОЙ РАБОТЫ №12 ===")
    engine = make_engine("sqlite://")
    engine.pool = StaticPool(creator=lambda: engine.raw_connection()) if False else engine.pool
    Base.metadata.create_all(engine)
    Session = make_session_factory(engine)
    with Session() as session:
        repository = SmartHomeRepository(session)
        service = SmartHomeService(repository)
        user = service.add_user("Иван", "ivan@example.com")
        print("USER:", user.id, user.name, user.email)
        sensor = service.add_device(user.id, "Датчик температуры", "TMP-001", "temperature", "online")
        lamp = service.add_device(user.id, "Лампа", "LAMP-001", "light", "offline")
        print("DEVICES:", [(d.id, d.name, d.status) for d in repository.list_devices()])
        service.save_measurement(sensor.id, 23.5, "online")
        service.save_measurement(sensor.id, 24.1, "online")
        print("MEASUREMENTS:", [(m.id, m.value) for m in repository.get_measurements(sensor.id)])
        print("FILTER online:", [d.name for d in repository.filter_devices(status="online")])
        print("SEARCH LAMP:", [d.name for d in repository.search_devices("LAMP")])
        service.change_device(lamp.id, status="online")
        print("UPDATED:", service.get_device(lamp.id).name, service.get_device(lamp.id).status)
        service.remove_device(lamp.id)
        print("FINAL:", [d.name for d in repository.list_devices()])
    print("Демонстрация завершена успешно.")


if __name__ == "__main__":
    main()
