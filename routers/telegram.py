# routers/telegram.py
# Telegram media download endpoint.
# Requires a valid pre-authorized session file (run encode_session.py first).
# Client connects lazily - no prompts at API startup.

import re
import io
import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from models.requests import TelegramDownloadRequest
from core.telegram_client import TelegramService
from core.dependencies import get_telegram_service

logger = logging.getLogger(__name__)
router = APIRouter()

# Matches: https://t.me/channelname/123
_TELEGRAM_URL_RE = re.compile(r"https?://t\.me/([^/]+)/(\d+)")


@router.post("/telegram/download")
async def download_telegram_media(
    request: TelegramDownloadRequest,
    service: TelegramService = Depends(get_telegram_service),
):
    """
    Download media from a public Telegram message URL.

    - **url**: Telegram message URL (e.g. https://t.me/channelname/123)

    Requires a pre-authorized Telethon session (run encode_session.py once to set up).
    """
    match = _TELEGRAM_URL_RE.match(request.url)
    if not match:
        raise HTTPException(
            status_code=400,
            detail="Invalid Telegram URL. Expected format: https://t.me/channelname/messageID",
        )

    chat_name = match.group(1)
    message_id = int(match.group(2))

    # Connect lazily (no-op if already connected)
    try:
        await service.ensure_connected()
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    try:
        client = service.client
        message = await client.get_messages(chat_name, ids=message_id)

        if not message or not message.media:
            raise HTTPException(
                status_code=404,
                detail="Message not found or contains no downloadable media.",
            )

        file_bytes = await message.download_media(file=bytes)

        # Determine MIME type and filename
        media_type = "application/octet-stream"
        filename = f"telegram_{chat_name}_{message_id}"

        if message.document:
            media_type = message.document.mime_type or media_type
            for attr in getattr(message.document, "attributes", []):
                if hasattr(attr, "file_name") and attr.file_name:
                    filename = attr.file_name
                    break

        logger.info(f"Streaming Telegram media: {filename} ({media_type})")

        return StreamingResponse(
            io.BytesIO(file_bytes),
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Telegram download error for {request.url}")
        raise HTTPException(status_code=500, detail=f"Telegram error: {str(e)}")
