from abc import ABC, abstractmethod


class AbstractRepositoryOperation(ABC):
    @abstractmethod
    async def addition(self, user_id: int, operation: dict):
        pass

    @abstractmethod
    async def subtraction(self, user_id: int, operation: dict):
        pass

    @abstractmethod
    async def transfer(self, user_id: int, transfer_wallets: dict):
        pass


class AbstractRepositoryOperationHistory(ABC):
    @abstractmethod
    async def add_history(self, updated_wallet: dict, income: bool, expense: bool):
        pass

    @abstractmethod
    async def add_transfer_history_between(self, from_wallet: dict, to_wallet: dict):
        pass

    @abstractmethod
    async def get_history(self, user_id: int, wallet_id: int | None, order_by_data: str, limit: int | None):
        pass
