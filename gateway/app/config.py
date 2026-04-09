from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SERVICE_NAME: str = "api-gateway"
    PORT: int = 8080
    DEBUG: bool = True

    # Сервисы
    USER_SERVICE_URL: str = "http://localhost:8001"
    SESSION_SERVICE_URL: str = "http://localhost:8002"
    VACANCIES_SERVICE_URL: str = "http://localhost:8003"

    # JWT для проверки токенов
    JWT_SECRET_KEY: str = "my-super-secret-key-change-me"
    JWT_ALGORITHM: str = "HS256"

    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    class Config:
        env_file = ".env"


settings = Settings()