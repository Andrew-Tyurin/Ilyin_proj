from abc import ABC, abstractmethod
from app.domain.dto import ExistingUserDTO, UserWithoutPasswDTO, CreateUserDTO


class AbstractRepositoryUser(ABC):
    @abstractmethod
    async def get_all(self, offset: int) -> list[UserWithoutPasswDTO]:
        pass

    @abstractmethod
    async def get_one(self, user_id: int) -> UserWithoutPasswDTO:
        pass

    @abstractmethod
    async def create(self, user: CreateUserDTO) -> UserWithoutPasswDTO:
        pass

    @abstractmethod
    async def authorization(self, user: ExistingUserDTO) -> UserWithoutPasswDTO:
        pass
