import os
from pathlib import Path

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


def build_path_to_env():
    base_dir = Path(__file__).resolve().parent.parent
    env_file = os.getenv("ENV_FILE", '.env')
    path_env_file = base_dir / env_file
    return path_env_file


class SettingsMainEnv(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=build_path_to_env(),
        env_file_encoding='utf-8',
        extra="ignore"
    )


class PsqlEnv(SettingsMainEnv):
    DATABASE_NAME: str | None = None
    DATABASE_USERNAME: str | None = None
    DATABASE_PASSWORD: str | None = None
    DATABASE_HOST: str | None = None
    DATABASE_PORT: str | None = None

    @property
    def async_db_url_str(self) -> PostgresDsn:
        return f'postgresql+asyncpg://{self.DATABASE_USERNAME}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}'


class SecretKeyEnv(SettingsMainEnv):
    SECRET_KEY: str | None = None


class Environment(SettingsMainEnv):
    APP_ENV: str | None = None


psql_env = PsqlEnv()
secret_key_env = SecretKeyEnv()
APP_ENV = Environment().APP_ENV
