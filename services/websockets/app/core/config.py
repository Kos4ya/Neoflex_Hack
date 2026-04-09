from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "collaboration-service"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8010

    ROOMS_SERVICE_URL: str = "http://rooms:8000"

    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"

    WS_PING_INTERVAL_SECONDS: int = 20
    SAVE_DEBOUNCE_SECONDS: float = 0.5
    FORCE_SAVE_INTERVAL_SECONDS: float = 5.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()