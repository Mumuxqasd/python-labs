from abc import ABC, abstractmethod

class Tariff(ABC):
    def __init__(self, name, base_fee):
        self.name = name
        self.base_fee = base_fee

    @property
    def base_fee(self):
        return self._base_fee

    @base_fee.setter
    def base_fee(self, value):
        value = float(value)
        if value < 0:
            raise ValueError("Абонентская плата не может быть отрицательной")
        self._base_fee = value

    @abstractmethod
    def calculate_cost(self):
        pass

    @abstractmethod
    def get_info(self):
        pass

    @abstractmethod
    def service_feature(self):
        pass

    def __str__(self):
        return self.get_info()

    def __lt__(self, other):
        if not isinstance(other, Tariff):
            return NotImplemented
        return self.calculate_cost() < other.calculate_cost()

    def __eq__(self, other):
        if not isinstance(other, Tariff):
            return NotImplemented
        return (
            self.name.lower(),
            round(self.calculate_cost(), 2),
        ) == (
            other.name.lower(),
            round(other.calculate_cost(), 2),
        )


class HomeTariff(Tariff):
    def __init__(self, name, base_fee, speed):
        super().__init__(name, base_fee)
        self.speed = speed

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        value = int(value)
        if value <= 0:
            raise ValueError("Скорость должна быть больше нуля")
        self._speed = value

    def calculate_cost(self):
        return self.base_fee + self.speed * 0.50

    def service_feature(self):
        return f"скорость {self.speed} Мбит/с"

    def get_info(self):
        return (
            f"Домашний тариф '{self.name}': {self.service_feature()}, "
            f"стоимость {self.calculate_cost():.2f} руб./мес."
        )


class BusinessTariff(Tariff):
    def __init__(self, name, base_fee, service_limit):
        super().__init__(name, base_fee)
        self.service_limit = service_limit

    @property
    def service_limit(self):
        return self._service_limit

    @service_limit.setter
    def service_limit(self, value):
        value = int(value)
        if value < 0:
            raise ValueError("Лимит дополнительных услуг не может быть отрицательным")
        self._service_limit = value

    def calculate_cost(self):
        return self.base_fee + self.service_limit * 120.0

    def service_feature(self):
        return f"лимит дополнительных услуг: {self.service_limit}"

    def get_info(self):
        return (
            f"Бизнес-тариф '{self.name}': {self.service_feature()}, "
            f"стоимость {self.calculate_cost():.2f} руб./мес."
        )


class PremiumBusinessTariff(BusinessTariff):
    def __init__(self, name, base_fee, service_limit, support_hours):
        super().__init__(name, base_fee, service_limit)
        self.support_hours = int(support_hours)
        if self.support_hours <= 0:
            raise ValueError("Число часов поддержки должно быть больше нуля")

    def calculate_cost(self):
        return super().calculate_cost() + self.support_hours * 50.0

    def service_feature(self):
        return (
            f"лимит услуг: {self.service_limit}, "
            f"премиум-поддержка: {self.support_hours} ч"
        )

    def get_info(self):
        return (
            f"Премиум-бизнес '{self.name}': {self.service_feature()}, "
            f"стоимость {self.calculate_cost():.2f} руб./мес."
        )


class ProviderIterator:
    def __init__(self, tariffs):
        self._tariffs = tariffs
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index >= len(self._tariffs):
            raise StopIteration
        item = self._tariffs[self._index]
        self._index += 1
        return item


class Provider:
    def __init__(self, name):
        self.name = name
        self._tariffs = []

    def add_tariff(self, tariff):
        if not isinstance(tariff, Tariff):
            raise TypeError("Можно добавлять только объекты Tariff")
        self._tariffs.append(tariff)

    def remove_tariff(self, index):
        if not 0 <= index < len(self._tariffs):
            raise IndexError("Тариф с таким номером не найден")
        return self._tariffs.pop(index)

    def edit_base_fee(self, index, new_fee):
        if not 0 <= index < len(self._tariffs):
            raise IndexError("Тариф с таким номером не найден")
        self._tariffs[index].base_fee = new_fee

    def total_monthly_cost(self):
        return sum(t.calculate_cost() for t in self._tariffs)

    def average_cost(self):
        if not self._tariffs:
            return 0.0
        return self.total_monthly_cost() / len(self._tariffs)

    def sort_tariffs(self):
        return sorted(self._tariffs)

    def search(self, name_part="", max_cost=None, tariff_type=None):
        result = []
        for tariff in self._tariffs:
            if name_part and name_part.lower() not in tariff.name.lower():
                continue
            if max_cost is not None and tariff.calculate_cost() > max_cost:
                continue
            if tariff_type is not None and not isinstance(tariff, tariff_type):
                continue
            result.append(tariff)
        return result

    def __iter__(self):
        return ProviderIterator(self._tariffs)

    def __len__(self):
        return len(self._tariffs)

    def __getitem__(self, index):
        return self._tariffs[index]


def read_float(prompt, minimum=0.0):
    while True:
        try:
            value = float(input(prompt).replace(",", "."))
            if value < minimum:
                raise ValueError
            return value
        except ValueError:
            print(f"Ошибка: введите число не меньше {minimum}.")


def read_int(prompt, minimum=0):
    while True:
        try:
            value = int(input(prompt))
            if value < minimum:
                raise ValueError
            return value
        except ValueError:
            print(f"Ошибка: введите целое число не меньше {minimum}.")

def create_tariff_interactive():
    print("1 — домашний, 2 — бизнес, 3 — премиум-бизнес")
    kind = input("Тип: ").strip()
    name = input("Название: ").strip() or "Без названия"
    fee = read_float("Базовая абонентская плата: ", 0.0)
    if kind == "1":
        return HomeTariff(name, fee, read_int("Скорость, Мбит/с: ", 1))
    if kind == "2":
        return BusinessTariff(name, fee, read_int("Лимит дополнительных услуг: ", 0))
    if kind == "3":
        return PremiumBusinessTariff(
            name,
            fee,
            read_int("Лимит дополнительных услуг: ", 0),
            read_int("Часы премиум-поддержки: ", 1),
        )
    raise ValueError("Неизвестный тип тарифа")

def show(provider):
    if not len(provider):
        print("Тарифов нет.")
        return
    for number, tariff in enumerate(provider, 1):
        print(f"{number}. {tariff.get_info()}")


def main():
    provider = Provider("Учебный интернет-провайдер")
    while True:
        print("\n===== ИНТЕРНЕТ-ПРОВАЙДЕР =====")
        print("1. Создать тариф")
        print("2. Показать тарифы")
        print("3. Рассчитать стоимость тарифа")
        print("4. Изменить базовую плату")
        print("5. Удалить тариф")
        print("6. Показать статистику")
        print("7. Сортировать тарифы по стоимости")
        print("8. Поиск по нескольким параметрам")
        print("0. Выход")
        choice = input("Выберите действие: ").strip()
        try:
            if choice == "1":
                provider.add_tariff(create_tariff_interactive())
                print("Тариф создан.")
            elif choice == "2":
                show(provider)
            elif choice == "3":
                show(provider)
                idx = read_int("Номер тарифа: ", 1) - 1
                print(f"Стоимость: {provider[idx].calculate_cost():.2f} руб./мес.")
            elif choice == "4":
                show(provider)
                idx = read_int("Номер тарифа: ", 1) - 1
                provider.edit_base_fee(idx, read_float("Новая базовая плата: ", 0.0))
                print("Состояние изменено.")
            elif choice == "5":
                show(provider)
                removed = provider.remove_tariff(read_int("Номер тарифа: ", 1) - 1)
                print("Удалён:", removed.name)
            elif choice == "6":
                print("Количество тарифов:", len(provider))
                print(f"Средняя итоговая стоимость: {provider.average_cost():.2f}")
                print(f"Сумма итоговых стоимостей: {provider.total_monthly_cost():.2f}")
            elif choice == "7":
                for tariff in provider.sort_tariffs():
                    print(tariff)
            elif choice == "8":
                name = input("Часть названия (можно пусто): ").strip()
                raw = input("Максимальная стоимость (можно пусто): ").strip()
                max_cost = float(raw.replace(",", ".")) if raw else None
                for tariff in provider.search(name, max_cost):
                    print(tariff)
            elif choice == "0":
                print("Работа программы завершена.")
                break
            else:
                print("Ошибка: неизвестный пункт меню.")
        except (ValueError, IndexError, TypeError) as error:
            print("Ошибка:", error)

if __name__ == "__main__":
    main()