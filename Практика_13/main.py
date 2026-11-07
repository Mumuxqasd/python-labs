from mongo_repository import MongoServerRepository
from redis_cache import RedisServerCache
from service import ServerMonitoringService


def main() -> None:
    service = ServerMonitoringService(MongoServerRepository(), RedisServerCache())
    while True:
        print("\n=== MONGODB + REDIS ===")
        print("1. Add")
        print("2. Find")
        print("3. List")
        print("4. Search")
        print("5. Update")
        print("6. Delete")
        print("7. Statistics")
        print("8. Cache status")
        print("9. Clear cache")
        print("10. Benchmark")
        print("0. Exit")
        choice = input("Выберите пункт: ").strip()
        if choice == "0":
            break
        try:
            if choice == "1":
                server_id = service.add_server({
                    "hostname": input("hostname: "),
                    "ip": input("IP: "),
                    "os_name": input("OS: "),
                    "characteristics": {},
                    "services": [],
                    "history": [],
                })
                print("ID:", server_id)
            elif choice == "2":
                print(service.get_server(input("ID: ").strip()))
            elif choice == "3":
                print(service.list_servers())
            elif choice == "4":
                print(service.search(input("Поиск: ").strip()))
            elif choice == "7":
                print(service.statistics())
            elif choice == "8":
                print(service.refresh_problem_cache())
            elif choice == "9":
                service.clear_cache()
                print("Кэш очищен")
            elif choice == "10":
                print(service.benchmark(input("ID: ").strip()))
            else:
                print("Для update/delete используйте demo.py или расширьте ввод данных")
        except Exception as error:
            print("Ошибка:", error)


if __name__ == "__main__":
    main()
