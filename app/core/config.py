from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Annotated, Any, Literal
from fastapi.security import OAuth2PasswordBearer
from fastapi_mail import ConnectionConfig
import os

from pydantic import (
    AnyUrl,
    BeforeValidator,
    computed_field,
    PostgresDsn,
    Field
)

from pydantic_core import MultiHostUrl


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra="ignore",
        env_ignore_empty = True,
    )
    DOMAIN: str = 'localhost'
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    PROJECT_NAME: str = "Taskify"

    FRONTEND_URL: str = Field(default="http://localhost:3000", description="URL of the frontend application")
    oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl="auth/login")
    INVITE_EXPIRATION_DAYS: int = 3

    @computed_field
    @property
    def server_host(self) -> str:
        # Use HTTPS for anything other than local development
        if self.ENVIRONMENT == "local":
            return f"http://{self.DOMAIN}"
        return f"https://{self.DOMAIN}"

    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = Field(default_factory=list)

    POSTGRESQL_USERNAME: str
    POSTGRESQL_PASSWORD: str
    POSTGRESQL_SERVER: str
    POSTGRESQL_PORT: int
    POSTGRESQL_DATABASE: str

    @computed_field  # type: ignore[misc]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRESQL_USERNAME,
            password=self.POSTGRESQL_PASSWORD,
            host=self.POSTGRESQL_SERVER,
            port=self.POSTGRESQL_PORT,
            path=self.POSTGRESQL_DATABASE,
        )
    

    EMAIL_ENABLED: bool = Field(default=True)

    SMTP_HOST: str = Field(default="smtp.gmail.com")
    SMTP_PORT: int = Field(default=587)
    SMTP_USERNAME: str 
    SMTP_PASSWORD: str 
    SMTP_SENDER_EMAIL: str

    @property
    def fastmail_config(self):
        return ConnectionConfig(
            MAIL_USERNAME=self.SMTP_USERNAME,
            MAIL_PASSWORD=self.SMTP_PASSWORD,
            MAIL_FROM=self.SMTP_SENDER_EMAIL,
            MAIL_PORT=self.SMTP_PORT,
            MAIL_SERVER=self.SMTP_HOST,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )
    

settings = Settings()
