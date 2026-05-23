# routers/tiktok.py
# TikTok video download endpoint.
# yt-dlp handles TikTok watermark removal natively.

from fastapi import APIRouter, BackgroundTasks
from services.downloader_service import YTDLPService
from models.requests import TikTokDownloadRequest

router = APIRouter()
downloader_service = YTDLPService()


@router.post("/tiktok/download")
async def download_tiktok_video(
    request: TikTokDownloadRequest,
    background_tasks: BackgroundTasks,
):
    """
    Download a TikTok video (watermark-free where possible).

    - **url**: Full TikTok video URL
    """
    custom_opts = {
        # Prefer the no-watermark stream yt-dlp exposes for TikTok
        "format": "bestvideo+bestaudio/best",
        "extractor_args": {
            "tiktok": {
                "webpage_download": ["true"],
            }
        },
    }

    result = downloader_service.download_video(
        url=request.url,
        background_tasks=background_tasks,
        custom_opts=custom_opts,
    )

    return result
