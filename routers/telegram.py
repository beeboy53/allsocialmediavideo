# routers/telegram.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from models.requests import TelegramDownloadRequest
from core.telegram_client import TelegramService
# Import the provider function from its new location
from core.dependencies import get_telegram_service
import re
import io

router = APIRouter()

@router.post("/telegram/download")
async def download_telegram_media(
    request: TelegramDownloadRequest,
    service: TelegramService = Depends(get_telegram_service)
):
    # ... the rest of your function code remains exactly the same ...
    # It will correctly receive the telegram_service instance via Depends()
    
    match = re.match(r"https?://t\.me/([^/]+)/(\d+)", request.url)
    if not match:
        raise HTTPException(status_code=400, detail="Invalid Telegram URL format.")
    
    chat_entity_name = match.group(1)
    message_id = int(match.group(2))

    try:
        client = service.client
        message = await client.get_messages(chat_entity_name, ids=message_id)

        if not message or not message.media:
            raise HTTPException(status_code=404, detail="Message not found or contains no media.")

        file_bytes = await message.download_media(file=bytes)
        
        media_type = 'application/octet-stream'
        filename = f"telegram_{chat_entity_name}_{message_id}"
        if message.document:
            media_type = message.document.mime_type
            attr = getattr(message.document, 'attributes', [])
            for a in attr:
                if hasattr(a, 'file_name'):
                    filename = a.file_name
                    break
        
        return StreamingResponse(
            io.BytesIO(file_bytes),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename=\"{filename}\""}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred with Telegram: {str(e)}")