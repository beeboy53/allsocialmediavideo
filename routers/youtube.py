# routers/youtube.py
# YouTube download endpoint.
# Cookies are loaded automatically from cookies/youtube.txt if valid.
# Resolution is optional - falls back gracefully if the requested height
# is not available for a given video.

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from services.downloader_service import YTDLPService
from models.requests import YouTubeDownloadRequest
from core.cookie_manager import get_cookie_file
import os

router = APIRouter()
downloader_service = YTDLPService()


def _build_format_string(resolution: str | None) -> str:
    """
    Builds a yt-dlp format string with a multi-level fallback chain.

    Chain (in priority order):
      1. Best video+audio at or below requested height, merged to mp4
      2. Best combined stream at or below requested height
      3. Best video+audio at any height
      4. Best combined stream (no height constraint)
      5. Absolute best available
    """
    if resolution:
        h = resolution.replace("p", "").strip()

        # Validate that the height value is numeric
        if not h.isdigit():
            raise HTTPException(
                status_code=400,
                detail=f"Invalid resolution '{resolution}'. Use a value like '720p' or '1080p'.",
            )

        return (
            f"bestvideo[ext=mp4][height<={h}]+bestaudio[ext=m4a]"
            f"/bestvideo[height<={h}]+bestaudio"
            f"/bestvideo[ext=mp4][height<={h}]+bestaudio"
            f"/best[height<={h}]"
            f"/bestvideo+bestaudio"
            f"/best[ext=mp4]"
            f"/best"
        )

    # No resolution requested - take the best available up to 1080p
    return (
        "bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]"
        "/bestvideo[height<=1080]+bestaudio"
        "/best[ext=mp4][height<=1080]"
        "/best[ext=mp4]"
        "/best"
    )


@router.post("/youtube/download")
async def download_youtube_video(
    request: YouTubeDownloadRequest,
    background_tasks: BackgroundTasks,
):
    """
    Download a YouTube video.

    - **url**: Full YouTube video URL
    - **resolution**: Optional. E.g. "720p", "1080p", "480p". Falls back to best available.
    """
    custom_opts: dict = {}

    # Format / resolution
    custom_opts["format"] = _build_format_string(request.resolution)

    # YouTube-specific extractor args to avoid throttling / format errors
    custom_opts["extractor_args"] = {
        "youtube": {
            "player_client": ["android", "web"],
            "player_skip": ["configs"],
        }
    }

    # Auto-load cookies if available
    cookie_path = get_cookie_file("youtube")
    if cookie_path:
        custom_opts["cookiefile"] = cookie_path

    result = downloader_service.download_video(
        url=request.url,
        background_tasks=background_tasks,
        custom_opts=custom_opts,
    )

    return result
