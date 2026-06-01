from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field, field_validator

from app.custom_enum import CurrencyEnum

CreateFieldDecimal = Annotated[Decimal, Field(ge=Decimal("0.01"), default=Decimal("0.01"))]
ReadFieldDecimal = Annotated[Decimal, Field(default=Decimal("0.00"))]


class BaseUserSchema(BaseModel):
    user_name: str = Field(..., min_length=3, max_length=80)
    password: str = Field(..., min_length=4, max_length=80)

    @field_validator("user_name", "password")
    @classmethod
    def invalid_characters(cls, value, info) -> str:
        field_name = info.field_name
        value = value.strip()

        if not value:
            raise ValueError(f"User fields '{field_name}' cannot be empty")

        invalid_characters_tuple = ('"', "'", ' ')
        for character in invalid_characters_tuple:
            if character in value:
                raise ValueError(f"User fields '{field_name}' invalid characters: {invalid_characters_tuple}")

        return value


class CreateWalletSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=80)
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
    amount: CreateFieldDecimal
    description: str | None = Field(None, min_length=1, max_length=80)

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
        return round(value, 2)


class CreateTransferWalletsShema(BaseModel):
    from_wallet_id: int = Field(ge=1)
    to_wallet_id: int = Field(ge=1)
    amount: CreateFieldDecimal

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
        return round(value, 2)


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
    balance: ReadFieldDecimal
    currency: CurrencyEnum
    user_id: int


class JustCreatedWalletSchema(BaseModel):
    message: str
    wallet: ReadWalletSchema


class ReadWalletsTotalBalanceSchema(BaseModel):
    user_id: int
    currency: CurrencyEnum
    total_balance: ReadFieldDecimal


class ReadOperationSchema(BaseModel):
    id: int
    type: str
    amount: ReadFieldDecimal
    description: str
    created_at: datetime


class ReadOperationsHistoryShema(BaseModel):
    wallet_id: int
    wallet_name: str
    currency: str
    operation: ReadOperationSchema


class ReadTransferBetweenWalletsShema(BaseModel):
    from_wallet: ReadOperationsHistoryShema
    to_wallet: ReadOperationsHistoryShema
