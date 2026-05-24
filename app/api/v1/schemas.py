from pydantic import BaseModel, Field, field_validator

from app.custom_enum import CurrencyEnum


class OperationSchema(BaseModel):
    wallet_name: str = Field(..., min_length=1, max_length=80)
    amount: int = Field(ge=1)
    description: str | None = Field(None, min_length=1, max_length=80)

    @field_validator("wallet_name", "description")
    @classmethod
    def fields_not_empty(cls, value, info) -> str:
        value = value.strip()
        if not value:
            raise ValueError(f"Wallet '{info.field_name}' cannot be empty")
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
    balance: int
    currency: CurrencyEnum


class ReadWalletsAllSchema(BaseModel):
    user_id: int
    user_name: str
    wallets: list[ReadWalletSchema]


class ReadWalletsTotalBalanceSchema(BaseModel):
    total_balance: int
