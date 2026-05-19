# core/dependencies.py

import os
from dotenv import load_dotenv
from .telegram_client import TelegramService

# Load environment variables from .env file
load_dotenv()

# Load credentials securely from environment variables
API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")

if not API_ID or not API_HASH:
    raise ValueError("TELEGRAM_API_ID and TELEGRAM_API_HASH must be set in .env")

# Create the single, shared instance of the TelegramService here
telegram_service = TelegramService(api_id=int(API_ID), api_hash=API_HASH)

# The dependency provider function
def get_telegram_service():
    return telegram_service