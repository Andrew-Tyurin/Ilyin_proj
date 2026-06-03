from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class UserWithoutPasswDTO:
    id: int
    user_name: str


@dataclass
class UserAuthorizationDTO:
    id: int
    user_name: str
    access_token: str


@dataclass
class TokenPayloadDTO:
    exp: int
    iat: int
    sub: int
    user_name: str


@dataclass
class UserLifetimeTokenDTO:
    id: int
    user_name: str
    expires_time_life: int


@dataclass
class WalletsTotalBalanceDTO:
    user_id: int
    currency: str
    total_balance: Decimal


@dataclass
class WalletDTO:
    id: int
    name: str
    balance: Decimal
    currency: str
    user_id: int


@dataclass
class WalletUpdateDTO:
    id: int | None = None
    name: str | None = None
    balance: Decimal | None = None
    currency: str | None = None
    user_id: int | None = None


@dataclass
class OperationDTO:
    id: int
    type: str
    amount: Decimal
    description: str
    created_at: datetime


@dataclass
class OperationHistoryDTO:
    wallet_id: int
    wallet_name: str
    currency: str
    operation: OperationDTO
