from fastapi import APIRouter, BackgroundTasks
from services.downloader_service import YTDLPService
from models.requests import TikTokDownloadRequest

router = APIRouter()
downloader_service = YTDLPService()

@router.post("/tiktok/download")
async def download_tiktok_video(request: TikTokDownloadRequest, background_tasks: BackgroundTasks):
    # [cite_start]No custom options are needed; default yt-dlp behavior removes watermarks [cite: 170]
    result = downloader_service.download_video(
        url=request.url,
        background_tasks=background_tasks
    )
    return result