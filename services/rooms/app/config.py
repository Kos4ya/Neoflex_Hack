# services/rooms/config.py
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Service
    SERVICE_NAME: str = "room-service"
    PORT: int = 8002
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@session-postgres:5432/room_db"
    DATABASE_ECHO: bool = False

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"  # Используем имя сервиса, а не localhost
    REDIS_PASSWORD: Optional[str] = None

    # JWT
    JWT_SECRET_KEY: str = "my-super-secret-key"  # Должен совпадать с gateway
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Other services
    USER_SERVICE_URL: str = "http://users:8001"  # Для вызова users сервиса

    # Security
    BCRYPT_ROUNDS: int = 12
    PASSWORD_MIN_LENGTH: int = 8

    # Rate Limiting
    RATE_LIMIT_LOGIN_ATTEMPTS: int = 5
    RATE_LIMIT_LOGIN_WINDOW_SECONDS: int = 900

    # Internal API
    INTERNAL_API_KEY: str = "internal-api-key"

    class Config:
        env_file = ".env"
        extra = "ignore"
        case_sensitive = True


settings = Settings()