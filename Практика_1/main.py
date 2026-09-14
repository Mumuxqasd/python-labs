def read_positive_int(prompt):
    while True:
        try:
            value = int(input(prompt))
            if value > 0:
                return value
            print(
                "Ошибка: значение должно быть больше нуля."
            )
        except ValueError:
            print("Ошибка: введите целое число.")


def read_nonnegative_float(prompt):
    while True:
        try:
            value = float(
                input(prompt).replace(",", ".")
            )
            if value >= 0:
                return value
            print(
                "Ошибка: значение не может быть "
                "отрицательным."
            )
        except ValueError:
            print("Ошибка: введите число.")


def calculate_average(values):
    total = 0
    for value in values:
        total += value
    return total / len(values)


def calculate_relative_spread(values):
    average = calculate_average(values)
    spread = max(values) - min(values)
    if average == 0:
        return 0.0
    return spread / average * 100


def determine_stability(
    download_speeds, upload_speeds
):
    download_spread = calculate_relative_spread(
        download_speeds
    )
    upload_spread = calculate_relative_spread(
        upload_speeds
    )
    max_spread = max(
        download_spread, upload_spread
    )
    if max_spread <= 20:
        stability = "стабильное"
    elif max_spread <= 50:
        stability = "умеренно стабильное"
    else:
        stability = "нестабильное"
    return (
        stability,
        download_spread,
        upload_spread,
    )


def count_below_threshold(
    download_speeds,
    upload_speeds,
    threshold,
):
    count = 0
    for i in range(len(download_speeds)):
        if (
            download_speeds[i] < threshold
            or upload_speeds[i] < threshold
        ):
            count += 1
    return count


def input_measurements(count):
    download_speeds = []
    upload_speeds = []
    for i in range(count):
        print(f"\nИзмерение {i + 1}:")
        download = read_nonnegative_float(
            "  Скорость загрузки, Мбит/с: "
        )
        upload = read_nonnegative_float(
            "  Скорость передачи, Мбит/с: "
        )
        download_speeds.append(download)
        upload_speeds.append(upload)
    return download_speeds, upload_speeds


def analyze_dataset(
    download_speeds,
    upload_speeds,
    threshold,
):
    (
        stability,
        download_spread,
        upload_spread,
    ) = determine_stability(
        download_speeds, upload_speeds
    )
    below_threshold = count_below_threshold(
        download_speeds,
        upload_speeds,
        threshold,
    )
    return {
        "avg_download": calculate_average(
            download_speeds
        ),
        "avg_upload": calculate_average(
            upload_speeds
        ),
        "max_download": max(download_speeds),
        "max_upload": max(upload_speeds),
        "min_download": min(download_speeds),
        "min_upload": min(upload_speeds),
        "below_threshold": below_threshold,
        "below_percent": (
            below_threshold
            / len(download_speeds)
            * 100
        ),
        "download_spread": download_spread,
        "upload_spread": upload_spread,
        "stability": stability,
    }


def print_dataset_results(dataset):
    result = dataset["result"]
    print(
        "\n========== РЕЗУЛЬТАТЫ АНАЛИЗА =========="
    )
    print(f"Набор данных: {dataset['number']}")
    print(
        "Количество измерений: "
        f"{len(dataset['download_speeds'])}"
    )
    print(
        "Средняя скорость загрузки: "
        f"{result['avg_download']:.2f} Мбит/с"
    )
    print(
        "Средняя скорость передачи: "
        f"{result['avg_upload']:.2f} Мбит/с"
    )
    print(
        "Максимальная скорость загрузки: "
        f"{result['max_download']:.2f} Мбит/с"
    )
    print(
        "Максимальная скорость передачи: "
        f"{result['max_upload']:.2f} Мбит/с"
    )
    print(
        "Минимальная скорость загрузки: "
        f"{result['min_download']:.2f} Мбит/с"
    )
    print(
        "Минимальная скорость передачи: "
        f"{result['min_upload']:.2f} Мбит/с"
    )
    print(
        "Измерений ниже порога "
        f"{dataset['threshold']:.2f} Мбит/с: "
        f"{result['below_threshold']}"
    )
    print(
        "Доля измерений ниже порога: "
        f"{result['below_percent']:.2f}%"
    )
    print(
        "Относительный разброс загрузки: "
        f"{result['download_spread']:.2f}%"
    )
    print(
        "Относительный разброс передачи: "
        f"{result['upload_spread']:.2f}%"
    )
    print(
        "Оценка стабильности соединения: "
        f"{result['stability']}"
    )
    print("=========================================")


def create_dataset(number):
    print(f"\n--- Набор данных {number} ---")
    count = read_positive_int(
        "Введите количество измерений: "
    )
    threshold = read_nonnegative_float(
        "Введите порог скорости, Мбит/с: "
    )
    download_speeds, upload_speeds = (
        input_measurements(count)
    )
    result = analyze_dataset(
        download_speeds,
        upload_speeds,
        threshold,
    )
    return {
        "number": number,
        "threshold": threshold,
        "download_speeds": download_speeds,
        "upload_speeds": upload_speeds,
        "result": result,
    }


def print_saved_datasets(datasets):
    if len(datasets) == 0:
        print(
            "\nСохранённых наборов данных пока нет."
        )
        return
    print(
        "\n========== СОХРАНЁННЫЕ НАБОРЫ =========="
    )
    for dataset in datasets:
        result = dataset["result"]
        print(
            f"Набор {dataset['number']}: измерений "
            f"{len(dataset['download_speeds'])}, "
            "средняя загрузка "
            f"{result['avg_download']:.2f} Мбит/с, "
            "средняя передача "
            f"{result['avg_upload']:.2f} Мбит/с, "
            "стабильность: "
            f"{result['stability']}"
        )
    print("=========================================")


def print_overall_statistics(datasets):
    if len(datasets) == 0:
        print(
            "\nСначала добавьте хотя бы один "
            "набор данных."
        )
        return
    all_downloads = []
    all_uploads = []
    total_below = 0
    for dataset in datasets:
        for value in dataset["download_speeds"]:
            all_downloads.append(value)
        for value in dataset["upload_speeds"]:
            all_uploads.append(value)
        total_below += dataset["result"][
            "below_threshold"
        ]
    best_download_dataset = datasets[0]
    best_upload_dataset = datasets[0]
    for dataset in datasets[1:]:
        current_download = dataset["result"][
            "avg_download"
        ]
        best_download = best_download_dataset[
            "result"
        ]["avg_download"]
        if current_download > best_download:
            best_download_dataset = dataset
        current_upload = dataset["result"][
            "avg_upload"
        ]
        best_upload = best_upload_dataset[
            "result"
        ]["avg_upload"]
        if current_upload > best_upload:
            best_upload_dataset = dataset
    print(
        "\n====== ОБЩАЯ СТАТИСТИКА ПО ВСЕМ "
        "НАБОРАМ ======"
    )
    print(f"Количество наборов: {len(datasets)}")
    print(
        "Общее количество измерений: "
        f"{len(all_downloads)}"
    )
    avg_download = calculate_average(all_downloads)
    avg_upload = calculate_average(all_uploads)
    print(
        "Средняя загрузка по всем измерениям: "
        f"{avg_download:.2f} Мбит/с"
    )
    print(
        "Средняя передача по всем измерениям: "
        f"{avg_upload:.2f} Мбит/с"
    )
    max_download = max(all_downloads)
    max_upload = max(all_uploads)
    print(
        "Максимальная загрузка среди всех "
        "измерений: "
        f"{max_download:.2f} Мбит/с"
    )
    print(
        "Максимальная передача среди всех "
        "измерений: "
        f"{max_upload:.2f} Мбит/с"
    )
    print(
        "Всего измерений ниже своих порогов: "
        f"{total_below}"
    )
    print(
        "Лучший набор по средней загрузке: "
        f"{best_download_dataset['number']}"
    )
    print(
        "Лучший набор по средней передаче: "
        f"{best_upload_dataset['number']}"
    )
    print(
        "========================"
        "========================"
    )


def main():
    datasets = []
    while True:
        print(
            "\n===== АНАЛИЗ СКОРОСТИ "
            "ИНТЕРНЕТ-СОЕДИНЕНИЯ ====="
        )
        print(
            "1. Добавить и проанализировать "
            "набор данных"
        )
        print("2. Показать сохранённые наборы")
        print("3. Показать общую статистику")
        print("4. Выход")
        choice = input(
            "Выберите действие: "
        ).strip()
        if choice == "1":
            dataset = create_dataset(
                len(datasets) + 1
            )
            datasets.append(dataset)
            print_dataset_results(dataset)
        elif choice == "2":
            print_saved_datasets(datasets)
        elif choice == "3":
            print_overall_statistics(datasets)
        elif choice == "4":
            print("Работа программы завершена.")
            break
        else:
            print(
                "Ошибка: выберите пункт от 1 до 4."
            )


if __name__ == "__main__":
    main()
