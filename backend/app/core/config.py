from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from dotenv import load_dotenv

backend_dir = Path(__file__).resolve().parent.parent.parent
env_path = backend_dir / ".env"
load_dotenv(env_path)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(env_path),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    APP_NAME: str = "Costa Rica Travel"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = ""

    DATABASE_URL: str = ""
    REDIS_URL: str = "redis://localhost:6379"
    SECRET_KEY: str = ""

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REGEX: str = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"

    BACKEND_CORS_ORIGINS: str = '["http://localhost:3000", "http://localhost:3003"]'

    @property
    def cors_origins_list(self) -> list[str]:
        import json
        return json.loads(self.BACKEND_CORS_ORIGINS)

    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_COMMISSION_RATE: float = 0.10

    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""
    CLOUDINARY_FOLDER_PREFIX: str = "costaricatravel"

    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "noreply@costaricatravel.dev"
    EMAIL_FROM_NAME: str = "Costa Rica Travel"

    # SMTP transport (used when RESEND_API_KEY is empty and USE_SMTP_IN_DEV is true)
    USE_SMTP_IN_DEV: bool = False
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = False

    BILLIONMAIL_URL: str = ""
    BILLIONMAIL_API_KEY: str = ""

    SENTRY_DSN: str = ""
    SENTRY_ENVIRONMENT: str = ""

    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    SITE_URL: str = "https://costaricatravel.dev"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_stripe_configured(self) -> bool:
        return bool(self.STRIPE_SECRET_KEY and self.STRIPE_SECRET_KEY != "sk_test_...")

    @property
    def is_stripe_test_mode(self) -> bool:
        if not self.STRIPE_SECRET_KEY:
            return True
        return self.STRIPE_SECRET_KEY.startswith("sk_test_") or self.STRIPE_SECRET_KEY == "sk_test_..."


settings = Settings()

if not settings.DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in .env file!")

if not settings.SECRET_KEY:
    raise ValueError(
        "SECRET_KEY must be set in .env file for security! "
        "Generate one with: python3 -c 'import secrets; print(secrets.token_hex(32))'"
    )

if len(settings.SECRET_KEY) < 32:
    raise ValueError(
        "SECRET_KEY must be at least 32 characters for adequate entropy. "
        "Generate a strong key with: python3 -c 'import secrets; print(secrets.token_hex(32))'"
    )
