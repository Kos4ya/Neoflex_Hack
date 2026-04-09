from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SERVICE_NAME: str = "user-service"
    PORT: int = 8001
    DEBUG: bool = True

    DATABASE_URL: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    BCRYPT_ROUNDS: int = 12

    class Config:
        env_file = ".env"
        extra = "ignore"
        case_sensitive = True


settings = Settings()