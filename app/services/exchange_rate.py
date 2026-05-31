from decimal import Decimal

import httpx

from app.custom_enum import CurrencyEnum

EXCHANGE_RATE_DICT: dict[tuple[str, str], Decimal] = {
    (CurrencyEnum.USD, CurrencyEnum.RUB): Decimal("75.00"),
    (CurrencyEnum.USD, CurrencyEnum.EUR): Decimal("0.85"),
    (CurrencyEnum.EUR, CurrencyEnum.RUB): Decimal("85.00"),
    (CurrencyEnum.EUR, CurrencyEnum.USD): Decimal("1.15"),
    (CurrencyEnum.RUB, CurrencyEnum.USD): Decimal("0.0134"),
    (CurrencyEnum.RUB, CurrencyEnum.EUR): Decimal("0.0118"),
}


async def get_exchange_rates_via_an_api(from_currency: CurrencyEnum, to_currency: CurrencyEnum):
    url = f"https://latest.currency-api.pages.dev/v1/currencies/{from_currency}.json"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=5)
        response.raise_for_status()  # raise except если статус код != 200
        data = response.json()
        currency_all = data[from_currency]
        exchange_rate: Decimal = Decimal(str(currency_all[to_currency]))
        return exchange_rate


async def get_exchange_rate(from_currency: CurrencyEnum, to_currency: CurrencyEnum) -> Decimal:
    if from_currency == to_currency:
        return Decimal("1.00")

    try:
        rate = await get_exchange_rates_via_an_api(from_currency, to_currency)
    except Exception:
        key = (from_currency, to_currency)
        return EXCHANGE_RATE_DICT.get(key)

    return rate
