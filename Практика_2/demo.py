from clinic import (
    calculate_statistics,
    filter_by_age,
    group_by_doctor,
    multi_filter,
    search_by_doctor,
    search_multiple,
    sort_by_duration,
    sort_by_two_parameters,
    unique_doctors,
)

patients = [
    {"name": "Иванов Иван", "age": 18, "doctor": "Терапевт", "room": 101, "duration": 15},
    {"name": "Петрова Анна", "age": 35, "doctor": "Кардиолог", "room": 205, "duration": 30},
    {"name": "Сидоров Пётр", "age": 67, "doctor": "Терапевт", "room": 101, "duration": 25},
    {"name": "Орлова Мария", "age": 0, "doctor": "Педиатр", "room": 112, "duration": 40},
    {"name": "Ким Алексей", "age": 42, "doctor": "Кардиолог", "room": 205, "duration": 20},
]

print("ТЕСТ 1. Обычный набор из 5 объектов")
print("Пациентов:", len(patients))
print("Терапевт:", [p["name"] for p in search_by_doctor(patients, "терапевт")])
print("Возраст 18..50:", [p["name"] for p in filter_by_age(patients, 18, 50)])
stats = calculate_statistics(patients)
print("Средний возраст:", f"{stats['average_age']:.2f}")
print("Самый долгий приём:", stats["longest"]["name"], stats["longest"]["duration"])
print("Врачи:", sorted(unique_doctors(patients)))
print("По длительности:", [p["name"] for p in sort_by_duration(patients)])
print("\nТЕСТ 2. Дубликаты параметра: Кардиологов =", len(search_by_doctor(patients, "кардиолог")))
print("ТЕСТ 3. Граничный возраст 0 найден =", any(p["age"] == 0 for p in patients))
print("ТЕСТ 4. Поиск отсутствующего врача =", search_by_doctor(patients, "Невролог"))
print("ТЕСТ 5. Пустая фильтрация 120..130 =", filter_by_age(patients, 120, 130))
print("\nДОПОЛНИТЕЛЬНЫЕ ВОЗМОЖНОСТИ")
print("Мультифильтр:", [p["name"] for p in multi_filter(patients, "кардио", 30, 50, 205)])
print("Два параметра сортировки:", [p["name"] for p in sort_by_two_parameters(patients)])
print("Расширенный поиск 'ив':", [p["name"] for p in search_multiple(patients, "ив")])
print("Группы:", {key: len(value) for key, value in group_by_doctor(patients).items()})