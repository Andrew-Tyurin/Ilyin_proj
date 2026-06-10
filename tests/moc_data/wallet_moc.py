from datetime import datetime
from decimal import Decimal
from typing import TypeAlias

from app.custom_enum import CurrencyEnum, OperationTypeEnum
from tests.moc_data.base_moc import BaseDataclassMoc

DecimalStr: TypeAlias = str


class CreateWalletDataclassMoc(BaseDataclassMoc):
    name: str
    currency: CurrencyEnum


class CreateFullWalletDataclassMoc(BaseDataclassMoc):
    name: str
    balance: Decimal
    currency: CurrencyEnum


class ReadWalletDataclassMoc(BaseDataclassMoc):
    id: int
    name: str
    balance: DecimalStr
    currency: CurrencyEnum
    user_id: int


class ResultCreateWalletDataclassMoc(BaseDataclassMoc):
    message: str
    wallet: ReadWalletDataclassMoc


class ReadSumBalanceWalletsDataclassMoc(BaseDataclassMoc):
    user_id: int
    currency: CurrencyEnum
    total_balance: DecimalStr


class UpdateWalletDataclassMoc(BaseDataclassMoc):
    wallet_id: int
    amount: Decimal
    description: str | None


class CreateOperationWalletDataclassMoc(BaseDataclassMoc):
    wallet_id: int
    type: OperationTypeEnum
    amount: Decimal
    description: str | None


class ReadOperationWalletDataclassMoc(BaseDataclassMoc):
    id: int
    type: OperationTypeEnum
    amount: DecimalStr
    description: str | None
    created_at: datetime


class ReadResultUpdateWalletDataclassMoc(BaseDataclassMoc):
    wallet_id: int
    wallet_name: str
    currency: CurrencyEnum
    operation: ReadOperationWalletDataclassMoc


class TransferBetweenWalletDataclassMoc(BaseDataclassMoc):
    from_wallet_id: int
    to_wallet_id: int
    amount: Decimal
