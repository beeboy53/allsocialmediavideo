# routers/youtube.py

from fastapi import APIRouter, BackgroundTasks
from services.downloader_service import YTDLPService
from models.requests import YouTubeDownloadRequest
import os

router = APIRouter()
downloader_service = YTDLPService()

COOKIE_FILE = os.path.join(
    os.path.dirname(__file__),
    "..",
    "cookies.txt"
)

@router.post("/youtube/download")
async def download_youtube_video(
    request: YouTubeDownloadRequest,
    background_tasks: BackgroundTasks
):
    custom_opts = {}

    # Resolution handling
    if request.resolution:
        resolution_val = request.resolution.replace('p', '')

        format_str = (
            f'bestvideo[height<={resolution_val}]'
            f'+bestaudio/'
            f'best[height<={resolution_val}]/'
            f'best'
        )

        custom_opts['format'] = format_str

    else:
        custom_opts['format'] = 'best'

    # Use local cookies automatically
    if os.path.exists(COOKIE_FILE):
        custom_opts['cookiefile'] = COOKIE_FILE

    result = downloader_service.download_video(
        request.url,
        background_tasks=background_tasks,
        custom_opts=custom_opts
    )

    return result