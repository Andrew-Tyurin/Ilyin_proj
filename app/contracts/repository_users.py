from abc import ABC, abstractmethod

from app.domain.dto import UserWithoutPasswDTO
from app.domain.entities import User


class AbstractRepositoryUser(ABC):
    @abstractmethod
    async def get_all(self, offset: int) -> list[UserWithoutPasswDTO]:
        pass

    @abstractmethod
    async def get_one(self, user_id: int) -> UserWithoutPasswDTO:
        pass

    @abstractmethod
    async def create(self, user: User) -> UserWithoutPasswDTO:
        pass

    @abstractmethod
    async def authorization(self, user: User) -> UserWithoutPasswDTO:
        pass
