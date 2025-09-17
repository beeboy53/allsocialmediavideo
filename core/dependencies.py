# core/dependencies.py

import os
import base64
from dotenv import load_dotenv
from .telegram_client import TelegramService

# --- NEW: Session Decoding Logic ---
# On Render, the session is loaded from an environment variable.
SESSION_STRING = os.getenv("TELEGRAM_SESSION_STRING")
if SESSION_STRING:
    try:
        # Decode the string back into bytes
        session_bytes = base64.b64decode(SESSION_STRING)
        # Write the bytes to the session file that Telethon will use
        with open("downloader_session.session", "wb") as session_file:
            session_file.write(session_bytes)
        print("Telegram session file created from environment variable.")
    except Exception as e:
        print(f"Error decoding session string: {e}")
# -----------------------------------

# Load environment variables from .env file for local development
load_dotenv()

# Load credentials securely from environment variables
API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")

if not API_ID or not API_HASH:
    raise ValueError("TELEGRAM_API_ID and TELEGRAM_API_HASH must be set in .env")

# Create the single, shared instance of the TelegramService
telegram_service = TelegramService(api_id=int(API_ID), api_hash=API_HASH)

# The dependency provider function
def get_telegram_service():
    return telegram_service
