import logging
from logging import config as logging_config

from pydantic import ConfigDict, IPvAnyAddress
from pydantic_settings import BaseSettings

from src.core.logger import LOGGING


class AppSettings(BaseSettings):
    app_title: str
    project_host: IPvAnyAddress
    project_port: int
    secret_key: str
    access_token_expire_seconds: int

    postgres_user: str
    postgres_password: str
    postgres_db: str
    db_host: IPvAnyAddress | str
    db_port: int
    postgres_test_db: str
    demo: bool

    model_config = ConfigDict(env_file='.env')

    @property
    def dsn(self) -> str:
        return (
            f'postgresql+asyncpg://{self.postgres_user}:'
            f'{self.postgres_password}@{self.db_host}:'
            f'{self.db_port}/{self.postgres_db}'
        )

    @property
    def dsn_test(self) -> str:
        return (
            f'postgresql+asyncpg://{self.postgres_user}:'
            f'{self.postgres_password}@{self.db_host}:'
            f'{self.db_port}/{self.postgres_test_db}'
        )

settings = AppSettings()
logging_config.dictConfig(LOGGING)
logger = logging.getLogger(settings.app_title)
