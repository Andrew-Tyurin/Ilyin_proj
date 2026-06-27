from decimal import Decimal
from typing import Callable, Awaitable

from sqlalchemy import select, and_, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.contracts.repository_wallets import AbstractRepositoryWallet
from app.custom_enum import CurrencyEnum, ExchangeRateProviderEnum
from app.domain.dto import WalletsTotalBalanceDTO, WalletDTO
from app.domain.entities import Wallet, WalletNotFoundError, WalletAlreadyExistsError, CreationLimitExceededWalletsError
from app.domain.rules import WalletRules
from app.infrastructure.sqlalchemy_models import WalletORM


class SqlAlchemyRepositoryWallet(AbstractRepositoryWallet):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_balance(self, user_id: int, **kwargs) -> WalletsTotalBalanceDTO:
        currency_const: CurrencyEnum = kwargs.get("currency", CurrencyEnum.RUB)
        exchange_func: Callable[
            [Decimal, CurrencyEnum, CurrencyEnum], Awaitable[tuple[Decimal, ExchangeRateProviderEnum]]
        ] = kwargs.get("exchange_func")

        short_wallets = (await self._session.execute(
            select(WalletORM.balance, WalletORM.currency)
            .where(WalletORM.user_id == user_id)
        )).all()

        converted_balance_and_providers =  [
            await exchange_func(row.balance, row.currency, currency_const) for row in short_wallets
        ]

        provider = ''
        total_balance = 0
        for converted_balance, row_provider in converted_balance_and_providers:
            total_balance += converted_balance
            if not provider:
                provider = row_provider
            elif row_provider != provider:
                # логика в том что, хоть один запрос provider отличается, значит данные не точны.
                provider = ExchangeRateProviderEnum.APP

        return WalletsTotalBalanceDTO(
            user_id=user_id,
            currency=currency_const,
            total_balance=total_balance,
            provider=provider if provider else ExchangeRateProviderEnum.NO_PROVIDER,
        )

    async def get(self, user_id: int, wallet_name: str) -> WalletDTO:
        stm = await self._session.execute(
            select(WalletORM.id, WalletORM.name, WalletORM.balance, WalletORM.currency, WalletORM.user_id)
            .where(and_(WalletORM.name == wallet_name, WalletORM.user_id == user_id))
        )
        wallet = stm.one_or_none()

        if wallet is None:
            raise WalletNotFoundError()

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
        count_wallets: int = await self._session.scalar(
            select(func.count(WalletORM.id))
            .where(WalletORM.user_id == wallet.user_id)
        )

        if count_wallets >= WalletRules.max_amount_wallets:
            raise CreationLimitExceededWalletsError()

        try:
            orm_wallet = WalletORM(user_id=wallet.user_id, name=wallet.name, currency=wallet.currency)
            self._session.add(orm_wallet)
            await self._session.flush()
        except IntegrityError:
            raise WalletAlreadyExistsError()

        return WalletDTO(**orm_wallet.model_dump())
