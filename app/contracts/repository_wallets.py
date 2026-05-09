from abc import ABC, abstractmethod


class AbstractRepositoryWallet(ABC):
    @abstractmethod
    async def get(self, user_id: int, wallet_name: str | None = None):
        pass

    @abstractmethod
    async def get_all(self, user_id: int):
        pass

    @abstractmethod
    async def add(self, user_id: int, wallet: dict):
        pass
