import os
from pathlib import Path

from pydantic import PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

_ROOT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ROOT_DIR / ".env",
        env_ignore_empty=True,
        extra="ignore",
    )
    PROJECT_NAME: str = "AutoApply"
    ROOT_DIR: Path = _ROOT_DIR
    DEBUG: bool = False
    LOG_TO_FILE: bool = True
    USER_EMAIL: str
    PASSWORD: str
    API_KEY: str
    OPENAI_API_KEY: str
    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432
    # TODO: Check if user can specify custom drivers, so that they would not break SQLAlchemy
    DRIVERNAME: str = "postgresql+psycopg"

    @computed_field
    @property
    def DATABASE_URI(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme=self.DRIVERNAME,
            username=self.POSTGRES_USERNAME,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )


settings = Settings()  # type: ignore
