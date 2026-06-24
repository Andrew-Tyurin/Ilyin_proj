from datetime import datetime, date
from decimal import Decimal
from typing import Annotated
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, Field, field_validator

from app.custom_enum import CurrencyEnum, ExchangeRateProviderEnum
from app.domain.rules import UserRules, WalletRules, WalletOperationRules

AmountOperationDecimal = Annotated[Decimal, Field(
    ge=WalletOperationRules.amount_min,
    default=WalletOperationRules.amount_min)
]
ImageDecimal = Annotated[Decimal, Field(default=WalletRules.balance_min)]


class BaseUserSchema(BaseModel):
    user_name: str = Field(
        ...,
        min_length=UserRules.user_name_min_length,
        max_length=UserRules.user_name_max_length
    )
    password: str = Field(
        ...,
        min_length=UserRules.password_min_length,
        max_length=UserRules.password_max_length
    )

    @field_validator("user_name", "password")
    @classmethod
    def invalid_characters(cls, value, info) -> str:
        field_name = info.field_name
        value = value.strip()

        if not value:
            raise ValueError(f"User fields '{field_name}' cannot be empty")

        for character in UserRules.invalid_characters:
            if character in value:
                raise ValueError(
                    f"User fields '{field_name}' invalid characters: {UserRules.invalid_characters}"
                )

        return value


class CreateWalletSchema(BaseModel):
    name: str = Field(
        ...,
        min_length=WalletRules.name_min_length,
        max_length=WalletRules.name_max_length
    )
    currency: CurrencyEnum = CurrencyEnum.RUB

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, value, info) -> str:
        value = value.strip()
        if not value:
            raise ValueError(f"Wallet '{info.field_name}' cannot be empty")
        return value


class CreateOperationSchema(BaseModel):
    wallet_id: int = Field(ge=1)
    amount: AmountOperationDecimal
    description: str | None = Field(
        None,
        min_length=WalletOperationRules.description_min_length,
        max_length=WalletOperationRules.description_max_length
    )

    @field_validator("description")
    @classmethod
    def fields_not_empty(cls, value, info) -> str:
        value = value.strip()
        if not value:
            raise ValueError(f"Wallet '{info.field_name}' cannot be empty")
        return value

    @field_validator("amount")
    @classmethod
    def round_number(cls, value: Decimal, info) -> Decimal:
        return round(value, WalletOperationRules.amount_length_after_point)


class CreateTransferWalletsShema(BaseModel):
    from_wallet_id: int = Field(ge=1)
    to_wallet_id: int = Field(ge=1)
    amount: AmountOperationDecimal

    @field_validator("to_wallet_id")
    @classmethod
    def wallets_must_differ(cls, to_wallet_id, info) -> int:
        from_wallet_id = info.data.get("from_wallet_id")
        if from_wallet_id == to_wallet_id:
            raise ValueError(f"same wallets ids; ({from_wallet_id=}) == ({to_wallet_id=}) - unacceptable")
        return to_wallet_id

    @field_validator("amount")
    @classmethod
    def round_number(cls, value: Decimal, info) -> Decimal:
        return round(value, WalletOperationRules.amount_length_after_point)


class DateFromDateToSchema(BaseModel):
    date_from: date
    date_to: date
    timezone: str

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError:
            raise ValueError("Unknown timezone")

        return value

    @field_validator("date_to")
    @classmethod
    def validate_date(cls, date_to, info) -> date:
        date_from = info.data.get("date_from")
        if date_from > date_to:
            raise ValueError("date_from must be less date_to")

        number_of_days = (date_to - date_from).days
        if number_of_days > WalletOperationRules.file_in_interval_days:
            raise ValueError(
                f"The range is too wide; you have {number_of_days} days, "
                f"but it should be no more than {WalletOperationRules.file_in_interval_days} days."
            )

        return date_to


class ReadUserSchema(BaseModel):
    id: int | None
    user_name: str


class ReadUserAndTokenSchema(ReadUserSchema):
    access_token: str


class ReadPayloadTokenSchema(BaseModel):
    id: int
    user_name: str
    expires_time_life: int


class ReadWalletSchema(BaseModel):
    id: int
    name: str
    balance: ImageDecimal
    currency: CurrencyEnum
    user_id: int


class JustCreatedWalletSchema(BaseModel):
    message: str
    wallet: ReadWalletSchema


class ReadWalletsTotalBalanceSchema(BaseModel):
    user_id: int
    currency: CurrencyEnum
    total_balance: ImageDecimal
    provider: ExchangeRateProviderEnum


class ReadOperationSchema(BaseModel):
    id: int
    type: str
    amount: ImageDecimal
    description: str | None
    created_at: datetime


class ReadOperationsHistorySchema(BaseModel):
    wallet_id: int
    wallet_name: str
    currency: str
    operation: ReadOperationSchema


class ReadTransferBetweenWalletsSchema(BaseModel):
    from_wallet: ReadOperationsHistorySchema
    to_wallet: ReadOperationsHistorySchema
    provider:  ExchangeRateProviderEnum
