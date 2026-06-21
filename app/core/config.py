from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "URL Shortener API"
    app_version: str = "1.0.0"
    environment: str = "development"
    log_level: str = "INFO"
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/url_shortener"

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str | None = None
    redis_db: int = 0
    redis_socket_timeout_seconds: float = 3.0

    short_code_length: int = Field(default=7, ge=4, le=10)
    id_block_size: int = Field(default=10_000, ge=1)
    redis_id_counter_key: str = "url_shortener:id_counter"
    redis_bloom_key: str = "url_shortener:bloom"
    redis_bloom_capacity: int = Field(default=1_000_000, ge=1)
    redis_bloom_error_rate: float = Field(default=0.01, gt=0, lt=1)

    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:7000",
    ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
