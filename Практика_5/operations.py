from functools import reduce


def filter_objects(objects, predicate):
    return filter(predicate, objects)

def transform_objects(objects, operation):
    return map(operation, objects)

def sort_objects(objects, key_function):
    return sorted(objects, key=key_function)

def filter_by_speed(tariffs, minimum_speed):
    return list(filter_objects(tariffs, lambda tariff: tariff.speed >= minimum_speed))

def tariff_names(tariffs):
    return list(transform_objects(tariffs, lambda tariff: tariff.name))

def sort_by_fee(tariffs):
    return sort_objects(tariffs, lambda tariff: tariff.monthly_fee)

def cheapest_tariff(tariffs):
    if not tariffs:
        return None
    return min(tariffs, key=lambda tariff: tariff.monthly_fee)

def has_exact_speed(tariffs, speed):
    return any(tariff.speed == speed for tariff in tariffs)

def all_fees_nonnegative(tariffs):
    return all(tariff.monthly_fee >= 0 for tariff in tariffs)

def client_counts_by_name(tariffs):
    return {tariff.name: tariff.clients for tariff in tariffs}

def total_clients(tariffs):
    return reduce(lambda total, tariff: total + tariff.clients, tariffs, 0)

def total_monthly_revenue(tariffs):
    return sum(tariff.monthly_fee * tariff.clients for tariff in tariffs)

def process(objects, predicate, transform, key_function):
    filtered = filter(predicate, objects)
    transformed = map(transform, filtered)
    ordered = sorted(transformed, key=key_function)
    return (item for item in ordered)
