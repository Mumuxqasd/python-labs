from exceptions import InvalidClientDataError

class TariffPlan:
    def __init__(self, name, speed, monthly_fee):
        self.name = str(name).strip()
        self.speed = int(speed)
        self.monthly_fee = float(monthly_fee)
        if not self.name or self.speed <= 0 or self.monthly_fee < 0:
            raise InvalidClientDataError("Некорректные параметры тарифа")

    def to_dict(self):
        return {
            "name": self.name,
            "speed": self.speed,
            "monthly_fee": self.monthly_fee,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data["speed"], data["monthly_fee"])

    def __str__(self):
        return f"{self.name}: {self.speed} Мбит/с, {self.monthly_fee:.2f} руб./мес."


class Client:
    def __init__(self, name, tariff, speed, monthly_fee, connected=False):
        self.name = str(name).strip()
        self.tariff = str(tariff).strip()
        self.speed = int(speed)
        self.monthly_fee = float(monthly_fee)
        self.connected = bool(connected)
        if not self.name or not self.tariff or self.speed <= 0 or self.monthly_fee < 0:
            raise InvalidClientDataError("Некорректные данные клиента")

    def apply_tariff(self, tariff_plan):
        self.tariff = tariff_plan.name
        self.speed = tariff_plan.speed
        self.monthly_fee = tariff_plan.monthly_fee

    def to_dict(self):
        return {
            "name": self.name,
            "tariff": self.tariff,
            "speed": self.speed,
            "monthly_fee": self.monthly_fee,
            "connected": self.connected,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["name"],
            data["tariff"],
            data["speed"],
            data["monthly_fee"],
            data.get("connected", False),
        )

    def __str__(self):
        status = "подключён" if self.connected else "отключён"
        return (
            f"{self.name} | {self.tariff} | {self.speed} Мбит/с | "
            f"{self.monthly_fee:.2f} руб./мес. | {status}"
        )
