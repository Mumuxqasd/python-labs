from time import perf_counter

class OperationContext:
    def __init__(self, name: str) -> None:
        self.name = name
        self.start = 0.0

    def __enter__(self) -> "OperationContext":
        self.start = perf_counter()
        print(f"[CONTEXT] начало: {self.name}")
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        elapsed = perf_counter() - self.start
        if exc_type is None:
            print(f"[CONTEXT] завершено за {elapsed:.6f} sec")
        else:
            print(f"[CONTEXT] ошибка: {exc_value}")
        return False