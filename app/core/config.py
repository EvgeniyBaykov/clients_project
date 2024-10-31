from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """Класс настроек приложения"""

    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    PATH_TO_AVATAR_WATERMARK: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool
    VALIDATE_CERTS: bool
    RATINGS_PER_DAY: int
    REFRESH_SECRET_KEY: str
    REFRESH_TOKEN_EXPIRE_MINUTES: int

    @property
    def db_url(self):
        """Функция возвращает адрес БД"""
        return f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:5432/{self.POSTGRES_DB}'

    class Config:
        env_file = ".env"


settings = Settings()
