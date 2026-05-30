from enum import StrEnum


class CurrencyEnum(StrEnum):
    RUB = "rub"
    USD = "usd"
    EUR = "eur"


class OperationTypeEnum(StrEnum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER_INCOME = "transfer_income"
    TRANSFER_EXPENSE = "transfer_expense"


class OperationOrderEnum(StrEnum):
    INCREASE = "increase"
    DECREASE = "decrease"
