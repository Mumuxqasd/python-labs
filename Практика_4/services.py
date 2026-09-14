import logging

from exceptions import (
    AlreadyConnectedError,
    AlreadyDisconnectedError,
    ClientNotFoundError,
    TariffNotFoundError,
)
from models import Client

class ProviderService:
    def __init__(self, clients=None, tariffs=None):
        self.clients = list(clients or [])
        self.tariffs = list(tariffs or [])

    def find_tariff(self, name):
        for tariff in self.tariffs:
            if tariff.name.lower() == name.lower():
                return tariff
        raise TariffNotFoundError(f"Тариф '{name}' не найден")

    def add_client(self, name, tariff_name):
        tariff = self.find_tariff(tariff_name)
        client = Client(name, tariff.name, tariff.speed, tariff.monthly_fee, False)
        self.clients.append(client)
        logging.info("Добавлен клиент: %s, тариф: %s", client.name, tariff.name)
        return client

    def find_clients(self, query):
        query = query.lower().strip()
        return [
            client
            for client in self.clients
            if query in client.name.lower() or query in client.tariff.lower()
        ]

    def get_client(self, index):
        if not 0 <= index < len(self.clients):
            raise ClientNotFoundError("Клиент с таким номером не найден")
        return self.clients[index]

    def change_tariff(self, index, tariff_name):
        client = self.get_client(index)
        tariff = self.find_tariff(tariff_name)
        old = client.tariff
        client.apply_tariff(tariff)
        logging.info("Клиент %s: тариф %s -> %s", client.name, old, tariff.name)

    def connect(self, index):
        client = self.get_client(index)
        if client.connected:
            raise AlreadyConnectedError("Клиент уже подключён")
        client.connected = True
        logging.info("Клиент подключён: %s", client.name)

    def disconnect(self, index):
        client = self.get_client(index)
        if not client.connected:
            raise AlreadyDisconnectedError("Клиент уже отключён")
        client.connected = False
        logging.info("Клиент отключён: %s", client.name)

    def delete_client(self, index):
        client = self.get_client(index)
        self.clients.pop(index)
        logging.info("Удалён клиент: %s", client.name)
        return client
