from generators import TariffIterator, laziness_demo, tariffs_in_speed_range
from main import sample_tariffs
from operations import (
    cheapest_tariff,
    client_counts_by_name,
    filter_by_speed,
    has_exact_speed,
    process,
    sort_by_fee,
    tariff_names,
    total_clients,
)

tariffs = sample_tariffs()
print("ОБЪЕКТЫ:", len(tariffs), "| типы:", sorted({type(t).__name__ for t in tariffs}))
print("filter >= 200:", [t.name for t in filter_by_speed(tariffs, 200)])
print("map названий:", tariff_names(tariffs))
print("sorted по плате:", [t.name for t in sort_by_fee(tariffs)])
print("Самый дешёвый:", cheapest_tariff(tariffs).name)
print("any скорость 300:", has_exact_speed(tariffs, 300))
print("comprehension:", client_counts_by_name(tariffs))
print("reduce, клиентов:", total_clients(tariffs))
print("\nГЕНЕРАТОР 100..300:")
gen = tariffs_in_speed_range(tariffs, 100, 300)
print(next(gen).name)
print(next(gen).name)
print(next(gen).name)
try:
    next(gen)
except StopIteration:
    print("StopIteration — генератор завершён")
print("\nСОБСТВЕННЫЙ ИТЕРАТОР:")
it = TariffIterator(tariffs)
print(next(it).name, "->", next(it).name)
print("\nЛЕНИВОСТЬ:", laziness_demo(100000))
print("\nКОНВЕЙЕР (скорость >= 100, transform tuple, sort по цене):")
result = process(
    tariffs,
    lambda t: t.speed >= 100,
    lambda t: (t.name, t.monthly_fee),
    lambda item: item[1],
)
print(list(result))
