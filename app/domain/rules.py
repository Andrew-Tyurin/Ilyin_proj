from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class UserRules:
    user_name_min_length: int = 4
    user_name_max_length: int = 80
    password_min_length: int = 4
    password_max_length: int = 120
    invalid_characters: tuple = ('"', "'", ' ', '\\', '/')


@dataclass(frozen=True)
class WalletRules:
    name_min_length: int = 2
    name_max_length: int = 80
    balance_min: Decimal = Decimal("0.00")
    balance_max: Decimal = Decimal("999_999_999_999.99")
    balance_length: int = 14
    balance_length_after_point: int = 2


@dataclass(frozen=True)
class WalletOperationRules:
    amount_min: Decimal = Decimal("0.01")
    amount_max: Decimal = WalletRules.balance_max
    amount_length: int = WalletRules.balance_length
    amount_length_after_point: int = WalletRules.balance_length_after_point
    description_min_length: int = 2
    description_max_length: int = 80
    file_in_interval_days: int = 365
