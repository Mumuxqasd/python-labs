from internet_provider_oop import BusinessTariff, HomeTariff, PremiumBusinessTariff, Provider

provider = Provider("DemoNet")
objects = [
    HomeTariff("Дом 100", 300, 100),
    BusinessTariff("Бизнес 5", 900, 5),
    PremiumBusinessTariff("Премиум", 1500, 10, 8),
]
for obj in objects:
    provider.add_tariff(obj)

print("ТЕСТ 1. Созданы объекты всех типов:", [type(x).__name__ for x in provider])
print("\nТЕСТ 2-3. Общий полиморфный метод get_info():")
for obj in provider:
    print("-", obj.get_info())
print("\nТЕСТ 4. Изменение состояния:")
provider.edit_base_fee(0, 350)
print(provider[0])
print("\nТЕСТ 5. Некорректное свойство:")
try:
    provider[0].base_fee = -1
except ValueError as error:
    print(type(error).__name__ + ":", error)
print("\nТЕСТ 6. Полиморфная коллекция, стоимости:", [x.calculate_cost() for x in provider])
print("ТЕСТ 7. Композиция Provider -> Tariff, количество:", len(provider))
print("\nДОПОЛНИТЕЛЬНО")
print("Сортировка (__lt__):", [x.name for x in provider.sort_tariffs()])
print("Поиск по имени и цене:", [x.name for x in provider.search("б", 2000)])
it = iter(provider)
print("Собственный итератор next():", next(it).name, "/", next(it).name)
print("Доп. класс + уровень наследования:", isinstance(provider[2], BusinessTariff))
