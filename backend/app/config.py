"""
Application configuration using pydantic-settings.
All environment variables are loaded and validated here.
"""
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "DevSEO"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Security
    SECRET_KEY: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Clerk Authentication
    CLERK_SECRET_KEY: Optional[str] = None
    CLERK_PUBLISHABLE_KEY: Optional[str] = None

    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str
    REDIS_CACHE_TTL: int = 3600  # 1 hour

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001"]

    # Stripe
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_PRICE_FREE: Optional[str] = None
    STRIPE_PRICE_PRO: Optional[str] = None
    STRIPE_PRICE_AGENCY: Optional[str] = None

    # SendGrid
    SENDGRID_API_KEY: Optional[str] = None
    SENDGRID_FROM_EMAIL: str = "noreply@devseo.io"
    SENDGRID_FROM_NAME: str = "DevSEO"

    # OpenAI
    OPENAI_API_KEY: Optional[str] = None

    # Anthropic Claude
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-sonnet-4-5-20250929"

    # Clerk JWKS
    CLERK_JWKS_URL: str = "https://actual-herring-54.clerk.accounts.dev/.well-known/jwks.json"

    # DataForSEO (Keyword tracking)
    DATAFORSEO_LOGIN: Optional[str] = None
    DATAFORSEO_PASSWORD: Optional[str] = None

    # AWS S3 (Report storage)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    S3_BUCKET: Optional[str] = None
    S3_REGION: str = "us-east-1"

    # Sentry (Error tracking)
    SENTRY_DSN: Optional[str] = None

    # PostHog (Analytics)
    POSTHOG_API_KEY: Optional[str] = None

    # Crawler Settings
    CRAWLER_USER_AGENT: str = "DevSEO-Bot/1.0 (+https://devseo.io/bot)"
    CRAWLER_MAX_REQUESTS_PER_SECOND: float = 2.0
    CRAWLER_TIMEOUT_SECONDS: int = 30
    CRAWLER_MAX_RETRIES: int = 3

    # Worker Settings
    WORKER_POLL_INTERVAL_SECONDS: int = 10  # Check for new jobs every 10 seconds

    # Plan Limits
    FREE_MAX_WEBSITES: int = 1
    FREE_MAX_SCANS_PER_MONTH: int = 1
    FREE_MAX_AI_SUGGESTIONS_PER_MONTH: int = 5
    FREE_MAX_KEYWORDS: int = 0
    FREE_MAX_PAGES_PER_SCAN: int = 10

    PRO_MAX_WEBSITES: int = 3
    PRO_MAX_SCANS_PER_MONTH: int = 4  # Weekly
    PRO_MAX_AI_SUGGESTIONS_PER_MONTH: int = 50
    PRO_MAX_KEYWORDS: int = 20
    PRO_MAX_PAGES_PER_SCAN: int = 50

    AGENCY_MAX_WEBSITES: int = 10
    AGENCY_MAX_SCANS_PER_MONTH: int = 30  # Daily
    AGENCY_MAX_AI_SUGGESTIONS_PER_MONTH: int = -1  # Unlimited
    AGENCY_MAX_KEYWORDS: int = 100
    AGENCY_MAX_PAGES_PER_SCAN: int = 200

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


# Global settings instance
settings = Settings()
