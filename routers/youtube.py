# routers/youtube.py
# YouTube download endpoint.
# Handles regular videos, Shorts, and age-restricted content.
# Cookies are loaded automatically from cookies/youtube.txt if valid.

from fastapi import APIRouter, BackgroundTasks, HTTPException
from services.downloader_service import YTDLPService
from models.requests import YouTubeDownloadRequest
from core.cookie_manager import get_cookie_file
import yt_dlp
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
downloader_service = YTDLPService()

# YouTube extractor args - use android+web clients to get all format types
_YT_EXTRACTOR_ARGS = {
    "youtube": {
        "player_client": ["android", "web"],
        "player_skip": ["configs"],
    }
}


def _is_shorts(url: str) -> bool:
    return "/shorts/" in url


def _probe_formats(url: str, base_opts: dict) -> list:
    """
    Quickly fetches the available format list for a URL without downloading.
    Returns a list of yt-dlp format dicts.
    """
    probe_opts = {**base_opts, "skip_download": True, "quiet": True, "no_warnings": True}
    try:
        with yt_dlp.YoutubeDL(probe_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get("formats") or []
    except Exception:
        return []


def _has_separate_streams(formats: list) -> bool:
    """
    Returns True if the video has separate video-only and audio-only streams
    (i.e. normal YouTube videos that need merging).
    Returns False for Shorts and videos that only have combined streams.
    """
    has_video_only = any(
        f.get("vcodec") not in (None, "none") and f.get("acodec") in (None, "none")
        for f in formats
    )
    has_audio_only = any(
        f.get("acodec") not in (None, "none") and f.get("vcodec") in (None, "none")
        for f in formats
    )
    return has_video_only and has_audio_only


def _build_format_string(resolution: str | None, has_separate: bool) -> str:
    """
    Builds the right yt-dlp format string based on whether the video
    has separate video+audio streams (regular YT) or only combined streams (Shorts).

    For combined-only videos (Shorts): never use the + merge syntax.
    For regular videos: full merge chain with height-constrained fallbacks.
    """
    if resolution:
        h = resolution.replace("p", "").strip()
        if not h.isdigit():
            raise HTTPException(
                status_code=400,
                detail=f"Invalid resolution '{resolution}'. Use a value like '720p' or '1080p'.",
            )

        if has_separate:
            # Regular video - use merge format with full fallback chain
            return (
                f"bestvideo[ext=mp4][height<={h}]+bestaudio[ext=m4a]"
                f"/bestvideo[height<={h}]+bestaudio"
                f"/bestvideo[ext=mp4][height<={h}]+bestaudio[ext=m4a]"
                f"/best[ext=mp4][height<={h}]"
                f"/best[height<={h}]"
                f"/bestvideo[ext=mp4]+bestaudio[ext=m4a]"
                f"/bestvideo+bestaudio"
                f"/best[ext=mp4]"
                f"/best"
            )
        else:
            # Shorts / combined-only - never use + merge syntax
            return (
                f"best[ext=mp4][height<={h}]"
                f"/best[height<={h}]"
                f"/best[ext=mp4]"
                f"/best"
            )

    # No resolution specified
    if has_separate:
        return (
            "bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]"
            "/bestvideo[height<=1080]+bestaudio"
            "/best[ext=mp4][height<=1080]"
            "/best[ext=mp4]"
            "/best"
        )
    else:
        # Shorts - combined streams only
        return (
            "best[ext=mp4][height<=1080]"
            "/best[height<=1080]"
            "/best[ext=mp4]"
            "/best"
        )


@router.post("/youtube/download")
async def download_youtube_video(
    request: YouTubeDownloadRequest,
    background_tasks: BackgroundTasks,
):
    """
    Download a YouTube video or Short.

    - **url**: Full YouTube video URL (including /shorts/ URLs)
    - **resolution**: Optional. E.g. "720p", "1080p", "480p". Falls back to best available.
    """
    # Base yt-dlp options shared between probe and download
    base_opts: dict = {
        "extractor_args": _YT_EXTRACTOR_ARGS,
    }

    cookie_path = get_cookie_file("youtube")
    if cookie_path:
        base_opts["cookiefile"] = cookie_path

    # --- Step 1: probe available formats (fast, no download) ---
    # This tells us whether we're dealing with a Shorts-style combined-only
    # video or a regular video with separate video+audio streams.
    formats = _probe_formats(request.url, base_opts)

    if formats:
        separate = _has_separate_streams(formats)
        logger.info(
            f"{'Shorts/combined' if not separate else 'Regular'} video detected: {request.url}"
        )
    else:
        # Probe failed (private, geo-blocked, etc.) - fall back to safe combined-first format
        separate = False
        logger.warning(f"Format probe failed for {request.url}, using combined-only fallback")

    # --- Step 2: build the right format string and download ---
    custom_opts = {
        **base_opts,
        "format": _build_format_string(request.resolution, separate),
    }

    result = downloader_service.download_video(
        url=request.url,
        background_tasks=background_tasks,
        custom_opts=custom_opts,
    )

    return result
