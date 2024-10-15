from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "pg"
    db_password: str = "pg"
    db_name: str = "postgres"

    @property
    def db_connection_string(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
