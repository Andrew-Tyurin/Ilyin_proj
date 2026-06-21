from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class User:
    user_name: str
    password: str
    id: int | None = None


@dataclass
class Wallet:
    name: str
    currency: str
    user_id: int
    user: User | None = None
    balance: Decimal = Decimal("0.00")
    id: int | None = None


@dataclass
class Operation:
    type: str
    amount: Decimal
    wallet_id: int
    wallet: Wallet | None = None
    created_at: datetime | None = None
    description: str | None = None
    id: int | None = None


class BaseDomainError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class UserAlreadyExistsError(Exception):
    pass


class UserIncorrectDataError(Exception):
    pass


class WalletNotFoundError(Exception):
    pass


class WalletAlreadyExistsError(Exception):
    pass


class WalletUpdateError(Exception):
    pass


class NoMoreThanDaysError(Exception):
    pass
