import tempfile
from pathlib import Path

from exceptions import AlreadyConnectedError, ClientNotFoundError
from models import Client, TariffPlan
from services import ProviderService
from storage import JsonRepository, export_clients_csv, import_clients_csv

with tempfile.TemporaryDirectory() as temp_dir:
    temp = Path(temp_dir)
    clients_repo = JsonRepository(temp / "clients.json", Client, temp / "backups")
    tariffs_repo = JsonRepository(temp / "tariffs.json", TariffPlan, temp / "backups")
    tariffs = [TariffPlan("Старт", 50, 450), TariffPlan("Дом 100", 100, 650)]
    service = ProviderService([], tariffs)

    print("1. Создание объектов")
    service.add_client("Иванов Иван", "Старт")
    service.add_client("Петрова Анна", "Дом 100")
    print(*service.clients, sep="\n")

    print("\n2. Изменение тарифа и подключение")
    service.change_tariff(0, "Дом 100")
    service.connect(0)
    print(service.clients[0])

    print("\n3. Поиск 'Анна'")
    print(service.find_clients("Анна")[0])

    print("\n4. Пользовательские исключения")
    try:
        service.connect(0)
    except AlreadyConnectedError as error:
        print(type(error).__name__ + ":", error)
    try:
        service.get_client(99)
    except ClientNotFoundError as error:
        print(type(error).__name__ + ":", error)

    print("\n5. JSON: save -> load")
    clients_repo.save(service.clients)
    tariffs_repo.save(service.tariffs)
    loaded = clients_repo.load()
    print("Загружено:", len(loaded), "|", loaded[0])

    print("\n6. CSV: export -> import")
    csv_path = temp / "clients.csv"
    export_clients_csv(service.clients, csv_path)
    imported = import_clients_csv(csv_path, Client)
    print("Импортировано:", len(imported), "|", imported[1])

    print("\n7. Резервная копия")
    clients_repo.save(service.clients)
    print("Backup-файлов:", len(list((temp / "backups").glob("clients_*.json"))))
