from telethon import TelegramClient
import os

class TelegramService:
    def __init__(self, api_id: int, api_hash: str, session_name: str = "downloader_session"):
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)

    async def connect(self):
        """Connects and authorizes the client."""
        print("Connecting Telegram client...")
        await self.client.start()
        print("Telegram client connected.")

    async def disconnect(self):
        """Disconnects the client."""
        print("Disconnecting Telegram client...")
        await self.client.disconnect()
        print("Telegram client disconnected.")