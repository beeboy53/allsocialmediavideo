# core/dependencies.py
# Provides shared service instances via FastAPI Depends().
# Telegram credentials are optional - missing env vars won't crash startup.

import os
import logging
from dotenv import load_dotenv
from .telegram_client import TelegramService
from .cookie_manager import ensure_cookie_files_exist

load_dotenv()
logger = logging.getLogger(__name__)

# Create cookie placeholder files on startup (safe no-op if they exist)
ensure_cookie_files_exist()

# --- Telegram setup (optional) ---
API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")

_telegram_service: TelegramService | None = None

if API_ID and API_HASH:
    try:
        _telegram_service = TelegramService(api_id=int(API_ID), api_hash=API_HASH)
        logger.info("TelegramService instance created (not yet connected).")
    except Exception as e:
        logger.warning(f"Could not create TelegramService: {e}")
else:
    logger.warning(
        "TELEGRAM_API_ID / TELEGRAM_API_HASH not set in .env - "
        "Telegram download endpoint will return 503."
    )


def get_telegram_service() -> TelegramService:
    """FastAPI dependency: returns the shared TelegramService or raises 503."""
    if _telegram_service is None:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=503,
            detail=(
                "Telegram is not configured. "
                "Set TELEGRAM_API_ID and TELEGRAM_API_HASH in your .env file."
            ),
        )
    return _telegram_service
