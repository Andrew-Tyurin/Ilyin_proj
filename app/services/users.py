from app.contracts.repository_users import AbstractRepositoryUser
from app.contracts.token_service import AbstractTokenService
from app.domain.dto import UserWithoutPasswDTO, ExistingUserDTO, UserAuthorizationDTO, CreateUserDTO


class ServiceUser:
    def __init__(
            self,
            repo_user: AbstractRepositoryUser,
            service_token: AbstractTokenService
    ):
        self._repo_user = repo_user
        self._service_token = service_token

    async def get_users(self, offset: int) -> list[UserWithoutPasswDTO]:
        return await self._repo_user.get_all(offset)

    async def get_user(self, user_id: int) -> UserWithoutPasswDTO:
        return await self._repo_user.get_one(user_id)

    async def create_user(self, user: CreateUserDTO) -> UserAuthorizationDTO:
        new_user = await self._repo_user.create(user)
        token = self._service_token.encode_token(new_user)
        user_authorization = UserAuthorizationDTO(
            id=new_user.id,
            user_name=new_user.user_name,
            access_token=token
        )
        return user_authorization

    async def user_authorization(self, user: ExistingUserDTO) -> UserAuthorizationDTO:
        existing_user = await self._repo_user.authorization(user)
        token = self._service_token.encode_token(existing_user)
        user_authorization = UserAuthorizationDTO(
            id=existing_user.id,
            user_name=existing_user.user_name,
            access_token=token
        )
        return user_authorization
