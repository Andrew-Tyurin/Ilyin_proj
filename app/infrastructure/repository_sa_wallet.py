import asyncio
from decimal import Decimal
from typing import Callable, Awaitable

from fastapi import HTTPException
from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.contracts.repository_wallets import AbstractRepositoryWallet
from app.custom_enum import CurrencyEnum
from app.domain.dto import WalletsTotalBalanceDTO, WalletDTO
from app.domain.entities import Wallet
from app.infrastructure.sqlalchemy_models import WalletORM


class SqlAlchemyRepositoryWallet(AbstractRepositoryWallet):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_balance(self, user_id: int, **kwargs) -> WalletsTotalBalanceDTO:
        currency_const: CurrencyEnum = kwargs.get("currency", CurrencyEnum.RUB)
        exchange_func: Callable[[str, str], Awaitable[Decimal]] = kwargs.get("exchange_func")

        result = (await self._session.execute(
            select(WalletORM.currency, WalletORM.balance)
            .where(WalletORM.user_id == user_id)
        )).all()

        rates = await asyncio.gather(*[exchange_func(row.currency, currency_const) for row in result])
        total_balance = round(sum(rate * row.balance for rate, row in zip(rates, result)), 2)
        return WalletsTotalBalanceDTO(user_id=user_id, currency=currency_const, total_balance=total_balance)

    async def get(self, user_id: int, wallet_name: str) -> WalletDTO:
        stm = await self._session.execute(
            select(WalletORM.id, WalletORM.name, WalletORM.balance, WalletORM.currency, WalletORM.user_id)
            .where(and_(WalletORM.name == wallet_name, WalletORM.user_id == user_id))
        )
        wallet = stm.one_or_none()

        if wallet is None:
            raise HTTPException(status_code=404, detail=f"Wallet '{wallet_name}' does not exist")

        return WalletDTO(**dict(wallet._mapping))

    async def get_all(self, user_id: int) -> list[WalletDTO]:
        wallets_stm = (
            select(WalletORM.id, WalletORM.name, WalletORM.balance, WalletORM.currency, WalletORM.user_id)
            .where(WalletORM.user_id == user_id)
            .order_by(WalletORM.id)
        )
        wallets_result = await self._session.execute(wallets_stm)
        return [WalletDTO(**dict(wallet._mapping)) for wallet in wallets_result]

    async def add(self, wallet: Wallet) -> WalletDTO:
        stm = (
            select(WalletORM.id)
            .where(and_(WalletORM.name == wallet.name, WalletORM.user_id == wallet.user_id))
            .exists()
        )
        is_wallet = await self._session.scalar(select(stm))

        if is_wallet:
            raise HTTPException(status_code=400, detail=f"Wallet '{wallet.name}' already exists")
        try:
            orm_wallet = WalletORM(user_id=wallet.user_id, name=wallet.name, currency=wallet.currency)
            self._session.add(orm_wallet)
            await self._session.commit()
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail=f"Problem with creation Wallet: {e.args[0]}")

        return WalletDTO(**orm_wallet.model_dump())
