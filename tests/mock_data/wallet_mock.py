from datetime import datetime
from decimal import Decimal
from typing import TypeAlias

from app.custom_enum import CurrencyEnum, OperationTypeEnum, ExchangeRateProviderEnum
from tests.mock_data.base_mock import BaseDataclassMock

DecimalStr: TypeAlias = str


class CreateWalletDataclassMock(BaseDataclassMock):
    name: str
    currency: CurrencyEnum


class CreateFullWalletDataclassMock(BaseDataclassMock):
    name: str
    balance: Decimal
    currency: CurrencyEnum


class ReadWalletDataclassMock(BaseDataclassMock):
    id: int
    name: str
    balance: DecimalStr
    currency: CurrencyEnum
    user_id: int


class ResultCreateWalletDataclassMock(BaseDataclassMock):
    message: str
    wallet: ReadWalletDataclassMock


class ReadSumBalanceWalletsDataclassMock(BaseDataclassMock):
    user_id: int
    currency: CurrencyEnum
    total_balance: DecimalStr
    provider: ExchangeRateProviderEnum


class UpdateWalletDataclassMock(BaseDataclassMock):
    wallet_id: int
    amount: Decimal
    description: str | None


class CreateOperationWalletDataclassMock(BaseDataclassMock):
    wallet_id: int
    type: OperationTypeEnum
    amount: Decimal
    description: str | None


class ReadOperationWalletDataclassMock(BaseDataclassMock):
    id: int
    type: OperationTypeEnum
    amount: DecimalStr
    description: str | None
    created_at: datetime


class ReadResultUpdateWalletDataclassMock(BaseDataclassMock):
    wallet_id: int
    wallet_name: str
    currency: CurrencyEnum
    operation: ReadOperationWalletDataclassMock


class TransferBetweenWalletDataclassMock(BaseDataclassMock):
    from_wallet_id: int
    to_wallet_id: int
    amount: Decimal
