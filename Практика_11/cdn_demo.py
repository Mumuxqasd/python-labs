from time import perf_counter

import requests


def check(url: str) -> None:
    start = perf_counter()
    response = requests.get(url, timeout=5)
    elapsed = perf_counter() - start
    print(url)
    print("HTTP:", response.status_code)
    print("Cache-Control:", response.headers.get("Cache-Control"))
    print("X-Cache-Mode:", response.headers.get("X-Cache-Mode"))
    print("Время:", f"{elapsed:.6f}")


def main() -> None:
    check("http://127.0.0.1:9100/cpu.svg")
    check("http://127.0.0.1:9101/cpu.svg")


if __name__ == "__main__":
    main()
