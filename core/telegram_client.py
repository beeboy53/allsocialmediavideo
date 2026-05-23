# core/telegram_client.py
# Telegram client wrapper using Telethon.
# IMPORTANT: The client does NOT connect at import time.
# Connection only happens when a /telegram/download request is made.
# This prevents "Please enter your phone" prompts at startup.

import os
import logging
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

logger = logging.getLogger(__name__)


class TelegramService:
    def __init__(self, api_id: int, api_hash: str, session_name: str = "downloader_session"):
        self.api_id = api_id
        self.api_hash = api_hash
        # Store session file in the download/ directory alongside the existing .session file
        session_path = os.path.join(
            os.path.dirname(__file__), "..", session_name
        )
        self.client = TelegramClient(session_path, self.api_id, self.api_hash)
        self._connected = False

    async def ensure_connected(self):
        """
        Connects only if not already connected.
        Raises RuntimeError if authentication is required (no valid session).
        The user must pre-authenticate by running encode_session.py once.
        """
        if self._connected and self.client.is_connected():
            return

        logger.info("Connecting Telegram client...")
        try:
            # connect() alone does not prompt for phone; start() does.
            # We use connect() and then check authorization separately.
            await self.client.connect()

            if not await self.client.is_user_authorized():
                await self.client.disconnect()
                raise RuntimeError(
                    "Telegram session is not authorized. "
                    "Run encode_session.py to authenticate and create a session file first."
                )

            self._connected = True
            logger.info("Telegram client connected and authorized.")

        except RuntimeError:
            raise
        except Exception as e:
            logger.error(f"Telegram connection error: {e}")
            raise RuntimeError(f"Could not connect to Telegram: {e}")

    async def disconnect(self):
        if self.client.is_connected():
            await self.client.disconnect()
            self._connected = False
            logger.info("Telegram client disconnected.")
