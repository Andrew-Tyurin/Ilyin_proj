from typing import Annotated, AsyncGenerator, TypeAlias

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.domain.dto import TokenPayloadDTO
from app.infrastructure.jwt_token_implementation import JWTokenImplementation
from app.infrastructure.render_files_implementation import ReportLabOperationFilesPDF
from app.infrastructure.repository_sa_operation import SqlAlchemyRepositoryOperation, \
    SqlAlchemyRepositoryOperationHistory
from app.infrastructure.repository_sa_users import SqlAlchemyRepositoryUser
from app.infrastructure.repository_sa_wallet import SqlAlchemyRepositoryWallet
from app.infrastructure.sqlalchemy_db import AsyncSessionLocal
from app.infrastructure.unit_of_work_sa import SqlAlchemyUnitOfWork
from app.services.exchange_rate import convert_using_exchange_rate
from app.services.operations import ServiceOperation
from app.services.users import ServiceUser
from app.services.wallets import ServiceWallet

InstanceJWToken = JWTokenImplementation()
InstanceReportLabOperationFilesPDF = ReportLabOperationFilesPDF()
Security = HTTPBearer(description=f"Need JWT for authorization.")
Token: TypeAlias = str


def get_service_token():
    return InstanceJWToken


TokenServiceDep = Annotated[JWTokenImplementation, Depends(get_service_token)]


def get_access_token(credentials: HTTPAuthorizationCredentials = Depends(Security)) -> Token:
    return credentials.credentials


AccessToken = Annotated[str, Depends(get_access_token)]


def get_payload(token: AccessToken, service_token: TokenServiceDep) -> TokenPayloadDTO:
    return service_token.decode_token(token)


PayloadAccessToken = Annotated[TokenPayloadDTO, Depends(get_payload)]


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()


AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]


def get_service_user(session: AsyncSessionDep, service_token: TokenServiceDep):
    repo_user = SqlAlchemyRepositoryUser(session)
    uow = SqlAlchemyUnitOfWork(session)
    return ServiceUser(repo_user=repo_user, service_token=service_token, uow=uow)


UserServiceDep = Annotated[ServiceUser, Depends(get_service_user)]


def get_service_wallet(session: AsyncSessionDep):
    repo = SqlAlchemyRepositoryWallet(session)
    uow = SqlAlchemyUnitOfWork(session)
    return ServiceWallet(repo=repo, exchange_func=convert_using_exchange_rate, uow=uow)


WalletServiceDep = Annotated[ServiceWallet, Depends(get_service_wallet)]


def get_service_operation(session: AsyncSessionDep):
    repo_operation = SqlAlchemyRepositoryOperation(session)
    repo_operation_history = SqlAlchemyRepositoryOperationHistory(session)
    uow = SqlAlchemyUnitOfWork(session)
    return ServiceOperation(
        repo_operation=repo_operation,
        repo_operation_history=repo_operation_history,
        exchange_func=convert_using_exchange_rate,
        uow=uow,
        render_files=InstanceReportLabOperationFilesPDF
    )


OperationServiceDep = Annotated[ServiceOperation, Depends(get_service_operation)]
