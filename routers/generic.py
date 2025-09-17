from fastapi import APIRouter, BackgroundTasks
from services.downloader_service import YTDLPService
from models.requests import GenericDownloadRequest

router = APIRouter()
downloader_service = YTDLPService()

@router.post("/generic/download")
async def download_generic_video(request: GenericDownloadRequest, background_tasks: BackgroundTasks):
    """
    Handles video downloads from any generic URL supported by yt-dlp.
    This serves as a fallback for non-social media links.
    """
    # No custom options are needed for the generic case
    result = downloader_service.download_video(
        url=request.url,
        background_tasks=background_tasks
    )
    return result