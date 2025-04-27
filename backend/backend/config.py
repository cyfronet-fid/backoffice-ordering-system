from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()  # This is to make the poetry run commands work with .env or if someone doesn't use PyCharm


class Settings(BaseSettings):
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "pg"
    db_password: str = "pg"
    db_name: str = "postgres"
    keycloak_host: str = "https://keycloak.docker-fid.grid.cyf-kr.edu.pl"
    keycloak_realm: str = "core"
    keycloak_client_id: str = "bos"
    api_key: str  # no default value is a best-practice here
    whitelabel_endpoint: str = "http://localhost:5000"
    whitelabel_client_key: str = ""  # Most likely the API Key of the SOMBO user in Whitelabel
    whitelabel_max_retry_delay_s: int = 60
    whitelabel_default_oms_id: int = 1

    @property
    def db_connection_string(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def keycloak_realm_base_url(self) -> str:
        return f"{self.keycloak_host}/realms/{self.keycloak_realm}"

    @property
    def keycloak_connection_string(self) -> str:
        return f"{self.keycloak_realm_base_url}/.well-known/openid-configuration"

    @property
    def keycloak_jwks_uri(self) -> str:
        return f"{self.keycloak_realm_base_url}/protocol/openid-connect/certs"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore
