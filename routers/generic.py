# routers/generic.py
# Generic video download endpoint - fallback for any yt-dlp-supported URL.

from fastapi import APIRouter, BackgroundTasks
from services.downloader_service import YTDLPService
from models.requests import GenericDownloadRequest

router = APIRouter()
downloader_service = YTDLPService()


@router.post("/generic/download")
async def download_generic_video(
    request: GenericDownloadRequest,
    background_tasks: BackgroundTasks,
):
    """
    Download a video from any URL supported by yt-dlp.
    Use this as a fallback when the specific platform endpoint isn't available.

    - **url**: Any yt-dlp-compatible video URL
    """
    result = downloader_service.download_video(
        url=request.url,
        background_tasks=background_tasks,
    )
    return result
