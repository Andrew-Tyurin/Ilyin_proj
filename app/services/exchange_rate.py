from decimal import Decimal
from time import perf_counter

import httpx

from app.custom_enum import CurrencyEnum

CACHE_LIFETIME = 120

EXCHANGE_RATE_DICT: dict[tuple[str, str], Decimal] = {
    (CurrencyEnum.USD, CurrencyEnum.RUB): Decimal("75.00"),
    (CurrencyEnum.USD, CurrencyEnum.EUR): Decimal("0.85"),
    (CurrencyEnum.EUR, CurrencyEnum.RUB): Decimal("85.00"),
    (CurrencyEnum.EUR, CurrencyEnum.USD): Decimal("1.15"),
    (CurrencyEnum.RUB, CurrencyEnum.USD): Decimal("0.0134"),
    (CurrencyEnum.RUB, CurrencyEnum.EUR): Decimal("0.0118"),
}
CACHE_EXCHANGE_RATE_DICT: dict[tuple[str, str], tuple[Decimal, float]] = {}


async def get_exchange_rates_via_an_api(from_currency: CurrencyEnum, to_currency: CurrencyEnum, url: str) -> Decimal:
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=5)
        response.raise_for_status()  # raise except если статус код != 200
        data = response.json()
        currency_all = data[from_currency]
        exchange_rate: Decimal = Decimal(str(currency_all[to_currency]))
        return exchange_rate


async def preparation_before_get_rate(from_currency: CurrencyEnum, to_currency: CurrencyEnum) -> Decimal | None:
    url_1 = f"https://latest.currency-api.pages.dev/v1/currencies/{from_currency}.json"
    url_2 = f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{from_currency}.json"
    for url in [url_1, url_2]:
        try:
            rate = await get_exchange_rates_via_an_api(from_currency, to_currency, url)
        except Exception:
            continue
        else:
            CACHE_EXCHANGE_RATE_DICT[(from_currency, to_currency)] = (rate, perf_counter())
            return rate

    return None


async def get_exchange_rate(from_currency: CurrencyEnum, to_currency: CurrencyEnum) -> Decimal:
    key = (from_currency, to_currency)

    if from_currency == to_currency:
        return Decimal("1.00")

    cache_exchange_rate = CACHE_EXCHANGE_RATE_DICT.get(key)
    if cache_exchange_rate:
        current_lifetime = int(perf_counter() - cache_exchange_rate[1])
        if current_lifetime > CACHE_LIFETIME:
            rate = await preparation_before_get_rate(from_currency, to_currency)
            if rate:
                return rate
        else:
            return cache_exchange_rate[0]
    else:
        rate = await preparation_before_get_rate(from_currency, to_currency)
        if rate:
            return rate

    return EXCHANGE_RATE_DICT.get(key)
