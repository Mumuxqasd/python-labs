class ProviderError(Exception):
    pass

class ClientNotFoundError(ProviderError):
    pass

class TariffNotFoundError(ProviderError):
    pass

class InvalidClientDataError(ProviderError):
    pass

class AlreadyConnectedError(ProviderError):
    pass

class AlreadyDisconnectedError(ProviderError):
    pass

class StorageError(ProviderError):
    pass