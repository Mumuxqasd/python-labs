import requests


BASE_URL = "http://127.0.0.1:8000"


def print_response(response) -> None:
    print("HTTP", response.status_code)
    if response.content:
        try:
            print(response.json())
        except ValueError:
            print(response.text)


def read_data() -> dict:
    return {
        "name": input("Имя: ").strip(),
        "host": input("Host: ").strip(),
        "status": input("Статус online/offline/maintenance: ").strip(),
        "cpu_load": float(input("CPU, %: ")),
    }


def main() -> None:
    while True:
        print("\n=== REST CLIENT ===")
        print("1. Список")
        print("2. Получить")
        print("3. Создать")
        print("4. PUT")
        print("5. PATCH CPU")
        print("6. Удалить")
        print("7. Фильтрация")
        print("8. Сортировка")
        print("9. Неработающие серверы")
        print("0. Выход")
        choice = input("Выберите пункт: ").strip()
        try:
            if choice == "1":
                response = requests.get(f"{BASE_URL}/servers", timeout=5)
            elif choice == "2":
                server_id = int(input("ID: "))
                response = requests.get(f"{BASE_URL}/servers/{server_id}", timeout=5)
            elif choice == "3":
                response = requests.post(f"{BASE_URL}/servers", json=read_data(), timeout=5)
            elif choice == "4":
                server_id = int(input("ID: "))
                response = requests.put(f"{BASE_URL}/servers/{server_id}", json=read_data(), timeout=5)
            elif choice == "5":
                server_id = int(input("ID: "))
                cpu = float(input("Новая загрузка CPU: "))
                response = requests.patch(f"{BASE_URL}/servers/{server_id}", json={"cpu_load": cpu}, timeout=5)
            elif choice == "6":
                server_id = int(input("ID: "))
                response = requests.delete(f"{BASE_URL}/servers/{server_id}", timeout=5)
            elif choice == "7":
                status = input("Статус: ").strip()
                response = requests.get(f"{BASE_URL}/servers", params={"status": status}, timeout=5)
            elif choice == "8":
                response = requests.get(f"{BASE_URL}/servers", params={"sort": "cpu_load", "order": "desc"}, timeout=5)
            elif choice == "9":
                response = requests.get(f"{BASE_URL}/servers/down", timeout=5)
            elif choice == "0":
                break
            else:
                print("Нет такого пункта")
                continue
            print_response(response)
        except (ValueError, requests.RequestException) as error:
            print("Ошибка:", error)


if __name__ == "__main__":
    main()
