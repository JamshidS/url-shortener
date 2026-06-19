from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application configuration settings."""
    
    database_url: str = "postgresql://user:password@localhost/dbname"
    # Other configuration settings can be added here as needed
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: Optional[str] = None


settings = Settings()