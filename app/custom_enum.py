from enum import StrEnum


class CurrencyEnum(StrEnum):
    RUB = "rub"
    USD = "usd"
    EUR = "eur"


class OperationEnum(StrEnum):
    INCOME = "income"
    EXPENSE = "expense"


class OperationOrderEnum(StrEnum):
    INCREASE = "increase"
    DECREASE = "decrease"
