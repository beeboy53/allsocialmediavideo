# routers/instagram.py
# Instagram media info and download endpoints.
# Handles single posts, Reels, and carousels.
# Returns direct URLs for the frontend to handle (video or image).

from fastapi import APIRouter, BackgroundTasks, HTTPException
from services.downloader_service import YTDLPService
from models.requests import InstagramDownloadRequest

router = APIRouter()
downloader_service = YTDLPService()


@router.get("/instagram/info")
async def get_instagram_info(url: str):
    """
    Extract metadata from an Instagram post, Reel, or carousel without downloading.

    Returns a list of media items (videos or images) with direct URLs.
    """
    info = downloader_service.extract_info(url)

    media_items = []

    # Carousels are returned as entries (playlist)
    entries = info.get("entries") or []
    if entries:
        for entry in entries:
            media_items.extend(_parse_entry(entry))
    else:
        media_items.extend(_parse_entry(info))

    if not media_items:
        raise HTTPException(
            status_code=422,
            detail="No downloadable media found for this Instagram URL.",
        )

    return {
        "title": info.get("title") or info.get("description") or "Instagram Post",
        "uploader": info.get("uploader") or info.get("channel") or "unknown",
        "media": media_items,
    }


@router.post("/instagram/download")
async def download_instagram_media(
    request: InstagramDownloadRequest,
    background_tasks: BackgroundTasks,
):
    """
    Download an Instagram video/Reel directly.

    - **url**: Full Instagram post or Reel URL
    """
    custom_opts = {
        "format": "bestvideo+bestaudio/best[ext=mp4]/best",
    }

    result = downloader_service.download_video(
        url=request.url,
        background_tasks=background_tasks,
        custom_opts=custom_opts,
    )

    return result


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def _best_thumbnail(thumbnails: list) -> str:
    if not thumbnails:
        return ""
    return thumbnails[-1].get("url", "")


def _parse_entry(entry: dict) -> list:
    items = []
    formats = entry.get("formats") or []
    has_video = any(f.get("vcodec") not in (None, "none") for f in formats)
    thumbnails = entry.get("thumbnails") or []
    thumbnail_url = _best_thumbnail(thumbnails) or entry.get("thumbnail", "")

    if has_video:
        video_url = _best_video_url(formats)
        if video_url:
            items.append({"type": "video", "url": video_url, "thumbnail": thumbnail_url})
    else:
        image_url = entry.get("url", "")
        if image_url:
            items.append({"type": "image", "url": image_url, "thumbnail": thumbnail_url or image_url})

    return items


def _best_video_url(formats: list) -> str:
    def has_video(f):
        return f.get("vcodec") not in (None, "none")

    def has_audio(f):
        return f.get("acodec") not in (None, "none")

    # 1. Combined mp4 (audio + video in one stream)
    combined_mp4 = [f for f in formats if has_video(f) and has_audio(f) and f.get("ext") == "mp4"]
    if combined_mp4:
        return max(combined_mp4, key=lambda f: f.get("height") or 0).get("url", "")

    # 2. Any combined stream
    combined = [f for f in formats if has_video(f) and has_audio(f)]
    if combined:
        return max(combined, key=lambda f: f.get("height") or 0).get("url", "")

    # 3. Video-only fallback
    video_only = [f for f in formats if has_video(f)]
    if video_only:
        return max(video_only, key=lambda f: f.get("height") or 0).get("url", "")

    return ""
