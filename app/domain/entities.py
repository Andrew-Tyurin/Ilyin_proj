from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class User:
    username: str
    password: str
    id: int | None = None


@dataclass
class Wallet:
    name: str
    balance: Decimal
    user: User
    currency: str
    id: int | None = None


@dataclass
class OperationWallet:
    wallet_id: int
    type: str
    amount: Decimal
    created_at: datetime
    wallet: Wallet
    description: str | None = None
    id: int | None = None
