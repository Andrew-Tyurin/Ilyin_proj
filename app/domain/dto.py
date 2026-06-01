from dataclasses import dataclass
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
