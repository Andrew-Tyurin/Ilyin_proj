from decimal import Decimal

from app.custom_enum import CurrencyEnum

TEST_EXCHANGE_RATE_DICT: dict[tuple[str, str], Decimal] = {
    (CurrencyEnum.USD, CurrencyEnum.RUB): Decimal("75.00"),
    (CurrencyEnum.USD, CurrencyEnum.EUR): Decimal("0.85"),
    (CurrencyEnum.EUR, CurrencyEnum.RUB): Decimal("85.00"),
    (CurrencyEnum.EUR, CurrencyEnum.USD): Decimal("1.15"),
    (CurrencyEnum.RUB, CurrencyEnum.USD): Decimal("0.0134"),
    (CurrencyEnum.RUB, CurrencyEnum.EUR): Decimal("0.0118"),
}


async def get_exchange_rate_replacement(from_currency: CurrencyEnum, to_currency: CurrencyEnum) -> Decimal:
    if from_currency == to_currency:
        return Decimal("1.00")

    key = (from_currency, to_currency)
    return TEST_EXCHANGE_RATE_DICT.get(key)
