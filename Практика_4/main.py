import argparse
import json
import logging
from pathlib import Path

from exceptions import ProviderError, StorageError
from models import Client, TariffPlan
from services import ProviderService
from storage import JsonRepository, export_clients_csv, import_clients_csv

BASE_DIR = Path(__file__).resolve().parent


def load_config():
    path = BASE_DIR / "config.json"
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def configure_logging(config):
    logging.basicConfig(
        filename=BASE_DIR / config["log_file"],
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        encoding="utf-8",
    )


def build_app():
    config = load_config()
    configure_logging(config)
    clients_repo = JsonRepository(
        BASE_DIR / config["clients_json"], Client, BASE_DIR / config["backup_dir"]
    )
    tariffs_repo = JsonRepository(
        BASE_DIR / config["tariffs_json"], TariffPlan, BASE_DIR / config["backup_dir"]
    )
    clients = clients_repo.load()
    tariffs = tariffs_repo.load()
    return config, clients_repo, tariffs_repo, ProviderService(clients, tariffs)


def save_all(service, clients_repo, tariffs_repo):
    clients_repo.save(service.clients)
    tariffs_repo.save(service.tariffs)


def show_clients(service):
    if not service.clients:
        print("Клиентов нет.")
        return
    for number, client in enumerate(service.clients, 1):
        print(f"{number}. {client}")


def show_tariffs(service):
    for tariff in service.tariffs:
        print("-", tariff)


def read_index(service):
    show_clients(service)
    try:
        return int(input("Номер клиента: ")) - 1
    except ValueError as error:
        raise ProviderError("Нужно ввести целый номер клиента") from error


def menu(config, clients_repo, tariffs_repo, service):
    csv_path = BASE_DIR / config["csv_file"]
    while True:
        print("\n===== УЧЁТ КЛИЕНТОВ ПРОВАЙДЕРА =====")
        print("1. Показать клиентов")
        print("2. Добавить клиента")
        print("3. Изменить тариф")
        print("4. Подключить клиента")
        print("5. Отключить клиента")
        print("6. Поиск")
        print("7. Удалить клиента")
        print("8. Сохранить JSON")
        print("9. Экспортировать CSV")
        print("10. Импортировать CSV")
        print("11. Показать тарифы")
        print("0. Выход")
        choice = input("Выберите действие: ").strip()
        try:
            if choice == "1":
                show_clients(service)
            elif choice == "2":
                show_tariffs(service)
                name = input("ФИО: ").strip()
                tariff = input("Название тарифа: ").strip()
                print("Добавлен:", service.add_client(name, tariff))
                clients_repo.save(service.clients)
            elif choice == "3":
                idx = read_index(service)
                show_tariffs(service)
                service.change_tariff(idx, input("Новый тариф: ").strip())
                clients_repo.save(service.clients)
                print("Тариф изменён.")
            elif choice == "4":
                service.connect(read_index(service))
                clients_repo.save(service.clients)
                print("Клиент подключён.")
            elif choice == "5":
                service.disconnect(read_index(service))
                clients_repo.save(service.clients)
                print("Клиент отключён.")
            elif choice == "6":
                found = service.find_clients(input("ФИО или тариф: "))
                for client in found:
                    print("-", client)
                if not found:
                    print("Совпадений нет.")
            elif choice == "7":
                print("Удалён:", service.delete_client(read_index(service)).name)
                clients_repo.save(service.clients)
            elif choice == "8":
                save_all(service, clients_repo, tariffs_repo)
                print("Данные сохранены.")
            elif choice == "9":
                export_clients_csv(service.clients, csv_path)
                print("CSV экспортирован:", csv_path)
            elif choice == "10":
                imported = import_clients_csv(csv_path, Client)
                service.clients = imported
                clients_repo.save(service.clients)
                logging.info("Импортировано из CSV клиентов: %d", len(imported))
                print("Импортировано клиентов:", len(imported))
            elif choice == "11":
                show_tariffs(service)
            elif choice == "0":
                save_all(service, clients_repo, tariffs_repo)
                print("Данные сохранены. Работа завершена.")
                return
            else:
                print("Ошибка: неизвестный пункт меню.")
        except (ProviderError, ValueError) as error:
            print("Ошибка:", error)


def build_parser():
    parser = argparse.ArgumentParser(description="Учёт клиентов интернет-провайдера")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("list")
    add = sub.add_parser("add")
    add.add_argument("name")
    add.add_argument("tariff")
    search = sub.add_parser("search")
    search.add_argument("query")
    for command in ("connect", "disconnect", "delete"):
        cmd = sub.add_parser(command)
        cmd.add_argument("index", type=int, help="Номер клиента, начиная с 1")
    change = sub.add_parser("change-tariff")
    change.add_argument("index", type=int)
    change.add_argument("tariff")
    sub.add_parser("export-csv")
    sub.add_parser("import-csv")
    return parser


def run_cli(args, config, clients_repo, tariffs_repo, service):
    csv_path = BASE_DIR / config["csv_file"]
    if args.command == "list":
        show_clients(service)
    elif args.command == "add":
        print(service.add_client(args.name, args.tariff))
        clients_repo.save(service.clients)
    elif args.command == "search":
        for client in service.find_clients(args.query):
            print(client)
    elif args.command == "connect":
        service.connect(args.index - 1)
        clients_repo.save(service.clients)
    elif args.command == "disconnect":
        service.disconnect(args.index - 1)
        clients_repo.save(service.clients)
    elif args.command == "delete":
        service.delete_client(args.index - 1)
        clients_repo.save(service.clients)
    elif args.command == "change-tariff":
        service.change_tariff(args.index - 1, args.tariff)
        clients_repo.save(service.clients)
    elif args.command == "export-csv":
        export_clients_csv(service.clients, csv_path)
        print(csv_path)
    elif args.command == "import-csv":
        service.clients = import_clients_csv(csv_path, Client)
        clients_repo.save(service.clients)

def main():
    try:
        config, clients_repo, tariffs_repo, service = build_app()
        args = build_parser().parse_args()
        if args.command:
            run_cli(args, config, clients_repo, tariffs_repo, service)
        else:
            menu(config, clients_repo, tariffs_repo, service)
    except StorageError as error:
        print("Ошибка хранилища:", error)
    except ProviderError as error:
        print("Ошибка:", error)


if __name__ == "__main__":
    main()
