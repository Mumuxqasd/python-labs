from generators import TariffIterator, laziness_demo, tariffs_in_speed_range
from models import BusinessTariff, HomeTariff
from operations import (
    all_fees_nonnegative,
    cheapest_tariff,
    client_counts_by_name,
    filter_by_speed,
    has_exact_speed,
    process,
    sort_by_fee,
    tariff_names,
    total_clients,
    total_monthly_revenue,
)


def sample_tariffs():
    return [
        HomeTariff("Старт", 50, 450, 300, 120),
        HomeTariff("Дом 100", 100, 650, 600, 240),
        HomeTariff("Игровой", 300, 990, 1000, 85),
        BusinessTariff("Бизнес S", 200, 1400, 1500, 35),
        BusinessTariff("Бизнес XL", 500, 2200, 5000, 18),
    ]


def read_int(prompt, minimum=0):
    while True:
        try:
            value = int(input(prompt))
            if value < minimum:
                raise ValueError
            return value
        except ValueError:
            print(f"Ошибка: введите целое число не меньше {minimum}.")


def show(items):
    items = list(items)
    if not items:
        print("Нет данных.")
    for item in items:
        print("-", item)


def main():
    tariffs = sample_tariffs()
    while True:
        print("\n===== ТАРИФЫ И ФУНКЦИОНАЛЬНЫЕ ВОЗМОЖНОСТИ =====")
        print("1. Показать тарифы")
        print("2. Фильтровать по скорости (filter + lambda)")
        print("3. Получить названия (map + lambda)")
        print("4. Сортировать по стоимости (sorted + key)")
        print("5. Найти самый дешёвый тариф")
        print("6. Проверить наличие заданной скорости (any)")
        print("7. Генератор диапазона скорости")
        print("8. Собственный итератор + next()")
        print("9. Статистика и comprehension")
        print("10. Демонстрация ленивости")
        print("11. Универсальный конвейер")
        print("0. Выход")
        choice = input("Выберите действие: ").strip()
        try:
            if choice == "1":
                show(tariffs)
            elif choice == "2":
                show(filter_by_speed(tariffs, read_int("Минимальная скорость: ", 1)))
            elif choice == "3":
                print(tariff_names(tariffs))
            elif choice == "4":
                show(sort_by_fee(tariffs))
            elif choice == "5":
                print(cheapest_tariff(tariffs))
            elif choice == "6":
                speed = read_int("Скорость: ", 1)
                print("Найдено." if has_exact_speed(tariffs, speed) else "Не найдено.")
            elif choice == "7":
                low = read_int("Скорость от: ", 1)
                high = read_int("Скорость до: ", low)
                generator = tariffs_in_speed_range(tariffs, low, high)
                show(generator)
            elif choice == "8":
                iterator = TariffIterator(tariffs)
                print("Первый:", next(iterator))
                print("Второй:", next(iterator))
                print("Оставшиеся:")
                for tariff in iterator:
                    print("-", tariff)
                try:
                    next(iterator)
                except StopIteration:
                    print("Итерация завершена: получен StopIteration.")
            elif choice == "9":
                print("Словарь клиентов:", client_counts_by_name(tariffs))
                print("Всего клиентов (reduce):", total_clients(tariffs))
                print(f"Расчётная месячная выручка: {total_monthly_revenue(tariffs):.2f}")
                print("Все платы неотрицательны:", all_fees_nonnegative(tariffs))
            elif choice == "10":
                result = laziness_demo()
                print("Размер списка, байт:", result["list_size"])
                print("Размер генератора, байт:", result["generator_size"])
                print("Первые три значения генератора:", result["first_three"])
            elif choice == "11":
                speed = read_int("Минимальная скорость: ", 1)
                pipeline = process(
                    tariffs,
                    lambda t: t.speed >= speed,
                    lambda t: (t.name, t.monthly_fee, t.speed),
                    lambda item: item[1],
                )
                print("Результат конвейера:")
                for item in pipeline:
                    print(item)
            elif choice == "0":
                print("Работа программы завершена.")
                break
            else:
                print("Ошибка: неизвестный пункт меню.")
        except (ValueError, TypeError) as error:
            print("Ошибка:", error)

if __name__ == "__main__":
    main()
