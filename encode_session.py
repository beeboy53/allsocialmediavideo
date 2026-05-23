#!/usr/bin/env python3
"""
encode_session.py
-----------------
Run this ONCE to authenticate with Telegram and create a session file.
After this runs successfully, the API will use the session file automatically
without prompting for a phone number.

Usage:
    python encode_session.py

Place the generated .session file in the download/ directory.
"""

import asyncio
import os
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession

load_dotenv()

API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")

if not API_ID or not API_HASH:
    print("ERROR: TELEGRAM_API_ID and TELEGRAM_API_HASH must be set in .env")
    exit(1)

SESSION_FILE = "downloader_session"


async def main():
    print(f"Creating Telegram session: {SESSION_FILE}.session")
    print("You will be prompted for your phone number and the code Telegram sends you.")
    print()

    client = TelegramClient(SESSION_FILE, int(API_ID), API_HASH)
    await client.start()

    me = await client.get_me()
    print(f"\n✅ Successfully authenticated as: {me.first_name} (@{me.username})")
    print(f"   Session saved to: {SESSION_FILE}.session")
    print("\nYou can now start the API server. It will use this session automatically.")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
