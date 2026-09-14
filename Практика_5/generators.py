import sys


def tariffs_in_speed_range(tariffs, minimum, maximum):
    for tariff in tariffs:
        if minimum <= tariff.speed <= maximum:
            yield tariff


class TariffIterator:
    def __init__(self, tariffs):
        self.tariffs = tariffs
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.tariffs):
            raise StopIteration
        result = self.tariffs[self.index]
        self.index += 1
        return result


def laziness_demo(size=100_000):
    list_result = [x * x for x in range(size)]
    generator_result = (x * x for x in range(size))
    return {
        "list_size": sys.getsizeof(list_result),
        "generator_size": sys.getsizeof(generator_result),
        "first_three": [next(generator_result) for _ in range(3)],
    }
