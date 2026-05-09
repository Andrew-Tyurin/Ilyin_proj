from abc import ABC, abstractmethod


class AbstractRepositoryOperation(ABC):
    @abstractmethod
    async def addition(self, user_id: int, operation: dict):
        pass

    @abstractmethod
    async def subtraction(self, user_id: int, operation: dict):
        pass
