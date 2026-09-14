from abc import ABC, abstractmethod

class Tariff(ABC):
    def __init__(self, name, speed, monthly_fee, limit, clients):
        self.name = str(name).strip()
        self.speed = int(speed)
        self.monthly_fee = float(monthly_fee)
        self.limit = int(limit)
        self.clients = int(clients)
        if not self.name:
            raise ValueError("Название не может быть пустым")
        if self.speed <= 0 or self.monthly_fee < 0 or self.limit < 0 or self.clients < 0:
            raise ValueError("Числовые значения тарифа некорректны")

    @abstractmethod
    def segment(self):
        pass

    def __str__(self):
        return (
            f"{self.name} [{self.segment()}]: скорость {self.speed} Мбит/с, "
            f"плата {self.monthly_fee:.2f}, лимит {self.limit}, клиентов {self.clients}"
        )


class HomeTariff(Tariff):
    def segment(self):
        return "домашний"


class BusinessTariff(Tariff):
    def segment(self):
        return "бизнес"
