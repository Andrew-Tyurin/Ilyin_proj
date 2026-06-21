from datetime import datetime
from decimal import Decimal
from typing import Callable, Awaitable

from sqlalchemy import update, and_, select, exists
from sqlalchemy.exc import IntegrityError, DBAPIError
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.contracts.repository_operations import AbstractRepositoryOperation, AbstractRepositoryOperationHistory
from app.custom_enum import OperationOrderEnum
from app.domain.dto import WalletUpdateDTO, OperationDTO, OperationHistoryDTO
from app.domain.entities import Operation, Wallet, WalletNotFoundError, WalletUpdateError
from app.infrastructure.sqlalchemy_models import WalletORM, OperationWalletORM


class SqlAlchemyRepositoryOperation(AbstractRepositoryOperation):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def addition(self, wallet: WalletUpdateDTO, add_amount: Decimal) -> Wallet:
        try:
            stmt = await self._session.execute(
                update(WalletORM)
                .where(and_(WalletORM.id == wallet.id, WalletORM.user_id == wallet.user_id))
                .values(balance=WalletORM.balance + add_amount)
                .returning(WalletORM.name, WalletORM.currency)
            )
            result = stmt.one_or_none()
        except (IntegrityError, DBAPIError):
            raise WalletUpdateError()

        if result is None:
            raise WalletNotFoundError()

        return Wallet(
            id=wallet.id,
            name=result.name,
            balance=add_amount,
            currency=result.currency,
            user_id=wallet.user_id,
        )

    async def subtraction(self, wallet: WalletUpdateDTO, subtract_to_balance: Decimal) -> Wallet:
        try:
            stmt = await self._session.execute(
                update(WalletORM)
                .where(and_(WalletORM.id == wallet.id, WalletORM.user_id == wallet.user_id))
                .values(balance=WalletORM.balance - subtract_to_balance)
                .returning(WalletORM.name, WalletORM.currency)
            )
            result = stmt.one_or_none()
        except IntegrityError:
            raise WalletUpdateError()

        if result is None:
            raise WalletNotFoundError()

        return Wallet(
            id=wallet.id,
            name=result.name,
            balance=subtract_to_balance,
            currency=result.currency,
            user_id=wallet.user_id,
        )

    async def transfer(
            self,
            from_wallet: WalletUpdateDTO,
            to_wallet: WalletUpdateDTO,
            amount: Decimal,
            **kwargs
    ) -> tuple[Wallet, Wallet]:
        exchange_func: Callable[[str, str], Awaitable[Decimal]] = kwargs.get("exchange_func")

        from_wallet_orm = await self._session.scalar(
            select(WalletORM)
            .where(and_(WalletORM.id == from_wallet.id, WalletORM.user_id == from_wallet.user_id))
        )
        to_wallet_orm = await self._session.scalar(
            select(WalletORM)
            .where(and_(WalletORM.id == to_wallet.id, WalletORM.user_id == to_wallet.user_id))
        )

        if from_wallet_orm is None:
            raise WalletNotFoundError(from_wallet.id)

        if to_wallet_orm is None:
            raise WalletNotFoundError(to_wallet.id)

        rate = await exchange_func(from_wallet_orm.currency, to_wallet_orm.currency)
        serialized_amount = round(amount * rate, 2)

        try:
            from_wallet_orm.balance -= amount
            await self._session.flush()
        except IntegrityError:
            raise WalletUpdateError(from_wallet.id)

        try:
            to_wallet_orm.balance += serialized_amount
            await self._session.flush()
        except (IntegrityError, DBAPIError):
            raise WalletUpdateError(to_wallet.id)

        from_wallet_updated = Wallet(
            id=from_wallet_orm.id,
            name=from_wallet_orm.name,
            balance=amount,
            currency=from_wallet_orm.currency,
            user_id=from_wallet_orm.user_id,
        )
        to_wallet_updated = Wallet(
            id=to_wallet_orm.id,
            name=to_wallet_orm.name,
            balance=serialized_amount,
            currency=to_wallet_orm.currency,
            user_id=to_wallet_orm.user_id,
        )
        return from_wallet_updated, to_wallet_updated


class SqlAlchemyRepositoryOperationHistory(AbstractRepositoryOperationHistory):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add_history(self, operation: Operation, wallet: Wallet) -> OperationHistoryDTO:
        wallet_name = wallet.name
        wallet_currency = wallet.currency

        wallet_id = operation.wallet_id
        amount = operation.amount
        description = operation.description
        operation_type = operation.type

        operation_orm = OperationWalletORM(
            wallet_id=wallet_id,
            type=operation_type,
            amount=amount,
            description=description,
        )
        self._session.add(operation_orm)
        await self._session.flush()

        operation = OperationDTO(
            id=operation_orm.id,
            type=operation_orm.type,
            amount=operation_orm.amount,
            description=operation_orm.description,
            created_at=operation_orm.created_at,
        )
        response_operation = OperationHistoryDTO(
            wallet_id=wallet_id,
            wallet_name=wallet_name,
            currency=wallet_currency,
            operation=operation,
        )
        return response_operation

    async def get_history(
            self,
            user_id: int,
            wallet_id: int | None,
            order_by_data: OperationOrderEnum,
            **kwargs
    ) -> list[OperationHistoryDTO]:
        limit: int = kwargs.get('limit')
        offset: int = kwargs.get('offset')

        stmt = (
            select(
                OperationWalletORM.wallet_id,
                WalletORM.name,
                WalletORM.currency,
                OperationWalletORM.id,
                OperationWalletORM.type,
                OperationWalletORM.amount,
                OperationWalletORM.description,
                OperationWalletORM.created_at,
            )
            .join(OperationWalletORM.wallet)
            .where(WalletORM.user_id == user_id)
            .limit(limit)
            .offset(offset)
        )

        if wallet_id:
            stm = (
                exists(WalletORM.id)
                .where(and_(WalletORM.id == wallet_id, WalletORM.user_id == user_id))
            )
            result_bool = await self._session.scalar(select(stm))
            if not result_bool:
                raise WalletNotFoundError()

            stmt = stmt.where(OperationWalletORM.wallet_id == wallet_id)

        if order_by_data == OperationOrderEnum.DECREASE:
            stmt = stmt.order_by(OperationWalletORM.id.desc())
        else:
            stmt = stmt.order_by(OperationWalletORM.id.asc())

        rows = (await self._session.execute(stmt)).all()

        response_operation_history = []
        for row in rows:
            operation = OperationDTO(
                id=row.id,
                type=row.type,
                amount=row.amount,
                description=row.description,
                created_at=row.created_at,
            )
            response_operation = OperationHistoryDTO(
                wallet_id=row.wallet_id,
                wallet_name=row.name,
                currency=row.currency,
                operation=operation,
            )
            response_operation_history.append(response_operation)
        return response_operation_history

    async def add_transfer_history_between(
            self,
            from_operation_and_wallet: tuple[Operation, Wallet],
            to_operation_and_wallet: tuple[Operation, Wallet]
    ) -> tuple[OperationHistoryDTO, OperationHistoryDTO]:
        operations_created_and_wallets: list[tuple] = []
        for operation, wallet in (from_operation_and_wallet, to_operation_and_wallet):
            operation_orm = OperationWalletORM(
                wallet_id=operation.wallet_id,
                type=operation.type,
                amount=operation.amount,
                description=operation.description,
            )
            self._session.add(operation_orm)
            operations_created_and_wallets.append((operation_orm, wallet))
        await self._session.flush()

        response_operation_history = []
        for operation, wallet in operations_created_and_wallets:
            operation = OperationDTO(
                id=operation.id,
                type=operation.type,
                amount=operation.amount,
                description=operation.description,
                created_at=operation.created_at,
            )
            response_operation = OperationHistoryDTO(
                wallet_id=wallet.id,
                wallet_name=wallet.name,
                currency=wallet.currency,
                operation=operation,
            )
            response_operation_history.append(response_operation)

        return tuple(response_operation_history)

    async def look_history_by_date(
            self,
            user_id: int,
            date_from: datetime,
            date_to: datetime
    ) -> list[OperationHistoryDTO]:

        stmt = (
            select(
                OperationWalletORM.wallet_id,
                WalletORM.name,
                WalletORM.currency,
                OperationWalletORM.id,
                OperationWalletORM.type,
                OperationWalletORM.amount,
                OperationWalletORM.description,
                OperationWalletORM.created_at,
            )
            .join(OperationWalletORM.wallet)
            .where(WalletORM.user_id == user_id)
            .where(OperationWalletORM.created_at.between(date_from, date_to))
            .order_by(OperationWalletORM.id.asc())
        )

        rows = (await self._session.execute(stmt)).all()

        response_operation_history = []
        for row in rows:
            operation = OperationDTO(
                id=row.id,
                type=row.type,
                amount=row.amount,
                description=row.description,
                created_at=row.created_at,
            )
            response_operation = OperationHistoryDTO(
                wallet_id=row.wallet_id,
                wallet_name=row.name,
                currency=row.currency,
                operation=operation,
            )
            response_operation_history.append(response_operation)

        return response_operation_history
