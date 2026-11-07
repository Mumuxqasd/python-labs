from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.repositories.repositories import SmartHomeRepository
from app.services.services import SmartHomeService


def main() -> None:
    print("=== ДЕМОНСТРАЦИЯ ЛАБОРАТОРНОЙ РАБОТЫ №15 ===")
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    with Session() as session:
        service = SmartHomeService(SmartHomeRepository(session))
        user = service.create_user("Иван", "ivan@example.com")
        first = service.create_device(user.id, "Датчик", "sensor", "Кухня", "online")
        second = service.create_device(user.id, "Лампа", "light", "Спальня", "offline")
        print("LIST:", [(d.id, d.name, d.room, d.status) for d in service.list_devices()])
        print("SEARCH:", [d.name for d in service.list_devices(search="Кух")])
        print("FILTER:", [d.name for d in service.list_devices(status="online")])
        service.add_measurement(first.id, 23.7)
        print("MEASUREMENTS:", [m.value for m in service.repository.measurements(first.id)])
        service.update_device(second.id, "Лампа потолочная", "Спальня", "online")
        print("UPDATED:", service.get_device(second.id).name, service.get_device(second.id).status)
        service.delete_device(second.id)
        print("FINAL:", [d.name for d in service.list_devices()])
    print("Web-интерфейс запускается командой python run.py после установки Flask.")
    print("Демонстрация завершена успешно.")


if __name__ == "__main__":
    main()
