from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.contracts.unit_of_work_interface import InterfaceUnitOfWork
from app.domain.entities import BaseDomainError


class SqlAlchemyUnitOfWork(InterfaceUnitOfWork):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def commit(self) -> None:
        try:
            await self._session.commit()
        except SQLAlchemyError:
            raise BaseDomainError()

    async def rollback(self) -> None:
        await self._session.rollback()
