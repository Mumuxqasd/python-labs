def read_nonempty(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Ошибка: значение не должно быть пустым.")

def read_int(prompt, minimum=0):
    while True:
        try:
            value = int(input(prompt))
            if value < minimum:
                print(f"Ошибка: значение должно быть не меньше {minimum}.")
                continue
            return value
        except ValueError:
            print("Ошибка: введите целое число.")

def add_patient(patients):
    patient = {
        "name": read_nonempty("ФИО пациента: "),
        "age": read_int("Возраст: ", 0),
        "doctor": read_nonempty("Специальность врача: "),
        "room": read_int("Номер кабинета: ", 1),
        "duration": read_int("Длительность приёма, мин: ", 1),
    }
    patients.append(patient)
    print("Пациент добавлен.")

def show_patients(patients, title="Список пациентов"):
    print(f"\n{title}")
    if not patients:
        print("Нет данных.")
        return
    for index, patient in enumerate(patients, 1):
        print(
            f"{index}. {patient['name']}; возраст: {patient['age']}; "
            f"врач: {patient['doctor']}; каб. {patient['room']}; "
            f"приём: {patient['duration']} мин"
        )

def search_by_doctor(patients, doctor):
    return [
        patient
        for patient in patients
        if doctor.lower() in patient["doctor"].lower()
    ]

def filter_by_age(patients, min_age, max_age):
    return [
        patient
        for patient in patients
        if min_age <= patient["age"] <= max_age
    ]

def sort_by_duration(patients):
    return sorted(patients, key=lambda patient: patient["duration"])


def calculate_statistics(patients):
    if not patients:
        return None
    ages = [patient["age"] for patient in patients]
    longest = max(patients, key=lambda patient: patient["duration"])
    shortest = min(patients, key=lambda patient: patient["duration"])
    return {
        "average_age": sum(ages) / len(ages),
        "min_age": min(ages),
        "max_age": max(ages),
        "longest": longest,
        "shortest": shortest,
        "average_duration": sum(p["duration"] for p in patients) / len(patients),
    }

def unique_doctors(patients):
    return {patient["doctor"] for patient in patients}

def delete_patient(patients, index):
    if 0 <= index < len(patients):
        removed = patients.pop(index)
        print(f"Удалён пациент: {removed['name']}.")
    else:
        print("Пациент с таким номером не найден.")

def edit_patient(patients, index):
    if not (0 <= index < len(patients)):
        print("Пациент с таким номером не найден.")
        return
    patient = patients[index]
    print("Оставьте строку пустой, чтобы сохранить текущее значение.")
    name = input(f"ФИО [{patient['name']}]: ").strip()
    doctor = input(f"Специальность врача [{patient['doctor']}]: ").strip()
    age = input(f"Возраст [{patient['age']}]: ").strip()
    room = input(f"Кабинет [{patient['room']}]: ").strip()
    duration = input(f"Длительность [{patient['duration']}]: ").strip()
    if name:
        patient["name"] = name
    if doctor:
        patient["doctor"] = doctor
    for key, raw, minimum in (("age", age, 0), ("room", room, 1), ("duration", duration, 1)):
        if raw:
            try:
                value = int(raw)
                if value < minimum:
                    raise ValueError
                patient[key] = value
            except ValueError:
                print(f"Поле {key} оставлено без изменений: введено некорректное значение.")
    print("Данные пациента обновлены.")

def multi_filter(patients, doctor="", min_age=0, max_age=200, room=None):
    return [
        patient
        for patient in patients
        if (not doctor or doctor.lower() in patient["doctor"].lower())
        and min_age <= patient["age"] <= max_age
        and (room is None or patient["room"] == room)
    ]

def sort_by_two_parameters(patients):
    return sorted(
        patients,
        key=lambda patient: (patient["doctor"].lower(), patient["duration"]),
    )

def search_multiple(patients, query):
    query = query.lower()
    return [
        patient
        for patient in patients
        if query in patient["name"].lower() or query in patient["doctor"].lower()
    ]

def group_by_doctor(patients):
    groups = {}
    for patient in patients:
        groups.setdefault(patient["doctor"], []).append(patient)
    return groups

def print_statistics(patients):
    stats = calculate_statistics(patients)
    if stats is None:
        print("Нет данных для статистики.")
        return
    print(f"Средний возраст: {stats['average_age']:.2f}")
    print(f"Минимальный возраст: {stats['min_age']}")
    print(f"Максимальный возраст: {stats['max_age']}")
    print(f"Средняя длительность приёма: {stats['average_duration']:.2f} мин")
    print(
        "Самый продолжительный приём: "
        f"{stats['longest']['name']} — {stats['longest']['duration']} мин"
    )
    print(
        "Самый короткий приём: "
        f"{stats['shortest']['name']} — {stats['shortest']['duration']} мин"
    )

def main():
    patients = []
    while True:
        print("\n===== ПОЛИКЛИНИКА =====")
        print("1. Добавить пациента")
        print("2. Показать пациентов")
        print("3. Найти пациентов по врачу")
        print("4. Фильтровать по возрасту")
        print("5. Сортировать по длительности")
        print("6. Показать статистику")
        print("7. Показать уникальные специальности врачей")
        print("8. Изменить пациента")
        print("9. Удалить пациента")
        print("10. Фильтрация по нескольким критериям")
        print("11. Сортировка по двум параметрам")
        print("12. Расширенный поиск")
        print("13. Группировка по врачу")
        print("0. Выход")
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            add_patient(patients)
        elif choice == "2":
            show_patients(patients)
        elif choice == "3":
            doctor = read_nonempty("Специальность врача: ")
            show_patients(search_by_doctor(patients, doctor), "Результат поиска")
        elif choice == "4":
            min_age = read_int("Минимальный возраст: ", 0)
            max_age = read_int("Максимальный возраст: ", min_age)
            show_patients(filter_by_age(patients, min_age, max_age), "Результат фильтрации")
        elif choice == "5":
            show_patients(sort_by_duration(patients), "Сортировка по длительности")
        elif choice == "6":
            print_statistics(patients)
        elif choice == "7":
            doctors = sorted(unique_doctors(patients))
            print("Уникальные специальности:", ", ".join(doctors) if doctors else "нет данных")
        elif choice == "8":
            show_patients(patients)
            edit_patient(patients, read_int("Номер пациента: ", 1) - 1)
        elif choice == "9":
            show_patients(patients)
            delete_patient(patients, read_int("Номер пациента: ", 1) - 1)
        elif choice == "10":
            doctor = input("Специальность (можно пусто): ").strip()
            min_age = read_int("Возраст от: ", 0)
            max_age = read_int("Возраст до: ", min_age)
            raw_room = input("Кабинет (можно пусто): ").strip()
            room = int(raw_room) if raw_room.isdigit() else None
            show_patients(multi_filter(patients, doctor, min_age, max_age, room), "Мультифильтр")
        elif choice == "11":
            show_patients(sort_by_two_parameters(patients), "Сортировка по врачу и длительности")
        elif choice == "12":
            query = read_nonempty("Строка поиска: ")
            show_patients(search_multiple(patients, query), "Расширенный поиск")
        elif choice == "13":
            groups = group_by_doctor(patients)
            if not groups:
                print("Нет данных.")
            for doctor, group in sorted(groups.items()):
                show_patients(group, f"Врач: {doctor}")
        elif choice == "0":
            print("Работа программы завершена.")
            break
        else:
            print("Ошибка: неизвестный пункт меню.")

if __name__ == "__main__":
    main()