from abc import ABC, abstractmethod

class AbstractRepositoryUser(ABC):
    @abstractmethod
    async def get_all(self, offset: int):
        pass

    @abstractmethod
    async def get_one(self, user_id: int):
        pass

    @abstractmethod
    async def create(self, user: dict):
        pass

    @abstractmethod
    async def authorization(self, user: dict):
        pass
