# routers/facebook.py
# Facebook video download endpoint.
# Cookies are loaded automatically from cookies/facebook.txt if valid.
# Cookies are no longer required in the request body.

from fastapi import APIRouter, BackgroundTasks
from services.downloader_service import YTDLPService
from models.requests import FacebookDownloadRequest
from core.cookie_manager import get_cookie_file

router = APIRouter()
downloader_service = YTDLPService()


@router.post("/facebook/download")
async def download_facebook_video(
    request: FacebookDownloadRequest,
    background_tasks: BackgroundTasks,
):
    """
    Download a Facebook video.

    - **url**: Full Facebook video URL
    
    Cookies are loaded automatically from cookies/facebook.txt.
    For private/login-required videos, populate that file with valid Netscape cookies.
    """
    custom_opts: dict = {
        # Facebook often serves best quality as a combined stream
        "format": "best[ext=mp4]/bestvideo+bestaudio/best",
    }

    # Auto-load Facebook cookies if available
    cookie_path = get_cookie_file("facebook")
    if cookie_path:
        custom_opts["cookiefile"] = cookie_path

    result = downloader_service.download_video(
        url=request.url,
        background_tasks=background_tasks,
        custom_opts=custom_opts,
    )

    return result
