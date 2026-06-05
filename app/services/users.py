from app.contracts.repository_users import AbstractRepositoryUser
from app.contracts.token_interface import InterfaceToken
from app.contracts.unit_of_work_interface import InterfaceUnitOfWork
from app.domain.dto import UserWithoutPasswDTO, UserAuthorizationDTO
from app.domain.entities import User


class ServiceUser:
    def __init__(
            self,
            repo_user: AbstractRepositoryUser,
            service_token: InterfaceToken,
            uow: InterfaceUnitOfWork
    ):
        self._repo_user = repo_user
        self._service_token = service_token
        self._uow = uow

    async def get_users(self, offset: int) -> list[UserWithoutPasswDTO]:
        return await self._repo_user.get_all(offset)

    async def get_user(self, user_id: int) -> UserWithoutPasswDTO:
        return await self._repo_user.get_one(user_id)

    async def create_user(self, user: User) -> UserAuthorizationDTO:
        new_user = await self._repo_user.create(user)
        await self._uow.commit()
        token = self._service_token.encode_token(new_user)
        user_authorization = UserAuthorizationDTO(
            id=new_user.id,
            user_name=new_user.user_name,
            access_token=token
        )
        return user_authorization

    async def user_authorization(self, user: User) -> UserAuthorizationDTO:
        existing_user = await self._repo_user.authorization(user)
        token = self._service_token.encode_token(existing_user)
        user_authorization = UserAuthorizationDTO(
            id=existing_user.id,
            user_name=existing_user.user_name,
            access_token=token
        )
        return user_authorization
