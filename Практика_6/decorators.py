from functools import wraps
from time import perf_counter
from typing import Any, Callable

def log_call(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        print(f"[LOG] вызван {func.__name__}()")
        return func(*args, **kwargs)

    return wrapper

def measure_time(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = perf_counter()
        result = func(*args, **kwargs)
        elapsed = perf_counter() - start
        print(f"[PERFORMANCE] {func.__name__}: {elapsed:.6f} sec")
        return result

    return wrapper

def action(title: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            print(f"[ACTION] {title}")
            return func(*args, **kwargs)

        return wrapper

    return decorator