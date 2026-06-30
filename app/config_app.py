import asyncio
from dataclasses import dataclass
from decimal import Decimal
from time import perf_counter

from app.config_env import secret_key_env, psql_env, APP_ENV


@dataclass(frozen=True)
class StartAppSettings:
    app: str = "app.main:app"
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    workers: int = 1


@dataclass(frozen=True)
class JWTokenSettings:
    secret_key: str = secret_key_env.SECRET_KEY
    time_minutes: int = 15
    algorithm: str = "HS256"


@dataclass(frozen=True)
class SaDbSettings:
    app_env: str | None = APP_ENV
    database_url: str = psql_env.async_db_url_str
    pool_size: int = 3
    max_overflow: int = 2
    echo: bool = False


@dataclass(frozen=True)
class ExchangeRateDefaultSettings:
    usd_to_rub: Decimal = Decimal("75.00")
    usd_to_eur: Decimal = Decimal("0.85")
    eur_to_rub: Decimal = Decimal("85.00")
    eur_to_usd: Decimal = Decimal("1.15")
    rub_to_usd: Decimal = Decimal("0.0134")
    rub_to_eur: Decimal = Decimal("0.0118")
    rub_to_rub: Decimal = Decimal("1.00")
    eur_to_eur: Decimal = Decimal("1.00")
    usd_to_usd: Decimal = Decimal("1.00")


@dataclass
class ExchangeRateApiSettings:
    cache_lifetime: int = 120
    timeout_response: int = 5
    lock_response: asyncio.Lock = asyncio.Lock()
    api_recovery_time_max: int = 40
    _api_start_recovery_time: int | float = 0

    def api_start_recovery_time(self) -> None:
        self._api_start_recovery_time = perf_counter()

    def api_default_recovery_time(self) -> None:
        self._api_start_recovery_time = 0

    @property
    def verification_of_recovery_time(self) -> bool:
        """
        Если _api_start_recovery_time != 0, значит api временно
        недоступно, где уже дали свой timeout к api, в течение которого даже
        не должны пытаться достучаться к api. Если _api_start_recovery_time == 0
        означает ограничений нет можно делать запросы к api, а если
        time_current > self.api_recovery_time_max
        значит время ожидания прошло, пробуем опять постучать к api.
        """
        if self._api_start_recovery_time:
            api_recovery_time_current = perf_counter() - self._api_start_recovery_time
            time_current = round(api_recovery_time_current)
            if time_current > self.api_recovery_time_max:
                self.api_default_recovery_time()
                return True
            return False

        return True


InstanceExchangeRateApiSettings = ExchangeRateApiSettings()
