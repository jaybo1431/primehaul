"""
Centralized configuration for PrimeHaul OS.

All environment variables are loaded and validated here.
Import `settings` from this module instead of calling os.getenv() directly.
"""

import os
import sys
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self):
        # --- Required (crash on startup if missing in production) ---
        self.DATABASE_URL: str = self._require("DATABASE_URL")
        self.JWT_SECRET_KEY: str = self._require("JWT_SECRET_KEY")
        self.SUPERADMIN_PASSWORD: str = self._require("SUPERADMIN_PASSWORD")
        self.SALES_PASSWORD: str = self._require("SALES_PASSWORD")

        # --- Optional with safe defaults ---
        self.APP_URL: str = os.getenv("APP_URL", "https://primehaul.co.uk")
        self.RAILWAY_PUBLIC_DOMAIN: str = os.getenv("RAILWAY_PUBLIC_DOMAIN", "localhost:8000")
        self.APP_ENV: str = os.getenv("APP_ENV", "development")
        self.STAGING_MODE: bool = os.getenv("STAGING_MODE", "false").lower() == "true"

        # Dev dashboard — default is OK for local dev, warn if using it
        self.DEV_DASHBOARD_PASSWORD: str = os.getenv("DEV_DASHBOARD_PASSWORD", "dev2025")
        if self.DEV_DASHBOARD_PASSWORD == "dev2025":
            logger.warning("DEV_DASHBOARD_PASSWORD is using the default value — set a strong password in production")

        # Mapbox
        self.MAPBOX_ACCESS_TOKEN: str = os.getenv("MAPBOX_ACCESS_TOKEN", "")

        # Stripe
        self.STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
        self.STRIPE_PRICE_ID: str = os.getenv("STRIPE_PRICE_ID", "")
        self.STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")

        # SMTP (PrimeHaul default)
        self.SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
        self.SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
        self.SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
        self.SMTP_FROM_EMAIL: str = os.getenv("SMTP_FROM_EMAIL", "noreply@primehaul.co.uk")
        self.SMTP_FROM_NAME: str = os.getenv("SMTP_FROM_NAME", "PrimeHaul")

        # Twilio
        self.TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
        self.TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
        self.TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "")
        self.TWILIO_ENABLED: bool = os.getenv("TWILIO_ENABLED", "false").lower() == "true"

        # OpenAI
        self.OPENAI_VISION_MODEL: str = os.getenv("OPENAI_VISION_MODEL", "gpt-4o-mini")

        # Sales
        self.SALES_AUTOMATION: bool = os.getenv("SALES_AUTOMATION", "false").lower() == "true"

        # Staging
        self.STAGING_USERNAME: str = os.getenv("STAGING_USERNAME", "primehaul")
        self.STAGING_PASSWORD: str = os.getenv("STAGING_PASSWORD", "changeme123")

    def _require(self, key: str) -> str:
        """Get a required env var or exit with a clear error."""
        value = os.getenv(key)
        if not value:
            logger.critical(f"FATAL: Required environment variable {key} is not set. Exiting.")
            sys.exit(1)
        return value


settings = Settings()
