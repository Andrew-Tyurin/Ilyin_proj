from app.contracts.repository_users import AbstractRepositoryUser
from app.contracts.token_service import AbstractTokenService


class ServiceUser:
    def __init__(
            self,
            repo_user: AbstractRepositoryUser,
            service_token: AbstractTokenService
    ):
        self._repo_user = repo_user
        self._service_token = service_token

    async def get_users(self, offset: int):
        return await self._repo_user.get_all(offset)

    async def get_user(self, user_id: int):
        return await self._repo_user.get_one(user_id)

    async def create_user(self, user: dict):
        new_user = await self._repo_user.create(user)
        token = self._service_token.encode_token(new_user)
        new_user["access_token"] = token
        return new_user

    async def user_authorization(self, user: dict):
        existing_user = await self._repo_user.authorization(user)
        token = self._service_token.encode_token(existing_user)
        existing_user["access_token"] = token
        return existing_user
