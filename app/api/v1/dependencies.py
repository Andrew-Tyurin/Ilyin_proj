from typing import Annotated, AsyncGenerator, TypeAlias

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.infrastructure.jwt_token_service import JWTokenService
from app.infrastructure.repository_sa_operation import SqlAlchemyRepositoryOperation
from app.infrastructure.repository_sa_users import SqlAlchemyRepositoryUser
from app.infrastructure.repository_sa_wallet import SqlAlchemyRepositoryWallet
from app.infrastructure.sqlalchemy_db import AsyncSessionLocal
from app.services.operations import ServiceOperation
from app.services.users import ServiceUser
from app.services.wallets import ServiceWallet

InstanceJWTokenService = JWTokenService()
Security = HTTPBearer(description=f"Need JWT for authorization.")
Token: TypeAlias = str


async def get_access_token(credentials: HTTPAuthorizationCredentials = Depends(Security)) -> Token:
    return credentials.credentials


async def get_payload(token: Annotated[str, Depends(get_access_token)]) -> dict:
    return InstanceJWTokenService.decode_token(token)


AccessToken = Annotated[str, Depends(get_access_token)]
PayloadAccessToken = Annotated[dict, Depends(get_payload)]


def get_service_token():
    return InstanceJWTokenService


TokenServiceDep = Annotated[JWTokenService, Depends(get_service_token)]


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]


def get_service_user(session: AsyncSessionDep, service_token: TokenServiceDep):
    repo_user = SqlAlchemyRepositoryUser(session)
    return ServiceUser(repo_user=repo_user, service_token=service_token)


UserServiceDep = Annotated[ServiceUser, Depends(get_service_user)]


def get_service_wallet(session: AsyncSessionDep):
    repo = SqlAlchemyRepositoryWallet(session)
    return ServiceWallet(repo)


WalletServiceDep = Annotated[ServiceWallet, Depends(get_service_wallet)]


def get_service_operation(session: AsyncSessionDep):
    repo = SqlAlchemyRepositoryOperation(session)
    return ServiceOperation(repo)


OperationServiceDep = Annotated[ServiceOperation, Depends(get_service_operation)]
