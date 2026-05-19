# routers/instagram.py

from fastapi import APIRouter, HTTPException
from services.downloader_service import YTDLPService

router = APIRouter()
downloader_service = YTDLPService()


@router.get("/instagram_info")
async def get_instagram_info(url: str):
    """
    Extracts metadata from an Instagram post, Reel, or carousel.
    Returns title, uploader, and a list of media items (video or image)
    in the format expected by the frontend JS.

    Query param:
        url (str): Full Instagram post/reel URL.

    Response shape:
        {
          "title": str,
          "uploader": str,
          "media": [
            { "type": "video"|"image", "url": str, "thumbnail": str }
          ]
        }
    """
    info = downloader_service.extract_info(url)

    media_items = []

    # Instagram carousels are returned as a playlist of entries
    entries = info.get("entries")
    if entries:
        for entry in entries:
            media_items.extend(_parse_entry(entry))
    else:
        # Single post or Reel
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


# --------------------------------------------------------------------------
# Internal helpers
# --------------------------------------------------------------------------

def _best_thumbnail(thumbnails: list) -> str:
    """Return the highest-resolution thumbnail URL from a thumbnails list."""
    if not thumbnails:
        return ""
    # yt-dlp orders thumbnails smallest → largest; take the last one
    return thumbnails[-1].get("url", "")


def _parse_entry(entry: dict) -> list:
    """
    Convert a single yt-dlp info dict into one or more media item dicts.
    Handles both video entries and image/photo entries.
    """
    items = []

    # Check if this is a video
    formats = entry.get("formats") or []
    has_video = any(f.get("vcodec") not in (None, "none") for f in formats)

    thumbnails = entry.get("thumbnails") or []
    thumbnail_url = _best_thumbnail(thumbnails) or entry.get("thumbnail", "")

    if has_video:
        # Pick the best mp4 format URL to hand directly to the browser
        video_url = _best_video_url(formats)
        if video_url:
            items.append({
                "type": "video",
                "url": video_url,
                "thumbnail": thumbnail_url,
            })
    else:
        # Image / photo post — the direct URL is in entry["url"]
        image_url = entry.get("url", "")
        if image_url:
            items.append({
                "type": "image",
                "url": image_url,
                "thumbnail": thumbnail_url or image_url,
            })

    return items


def _best_video_url(formats: list) -> str:
    """
    Pick the best direct video URL from yt-dlp's format list.
    Prefers a combined audio+video mp4 stream to avoid needing ffmpeg on the
    client side.  Falls back to the highest-quality format available.
    """
    # 1. Combined a/v mp4 streams (no merging needed)
    combined = [
        f for f in formats
        if f.get("vcodec") not in (None, "none")
        and f.get("acodec") not in (None, "none")
        and f.get("ext") == "mp4"
    ]
    if combined:
        best = max(combined, key=lambda f: f.get("height") or 0)
        return best.get("url", "")

    # 2. Any combined stream
    combined_any = [
        f for f in formats
        if f.get("vcodec") not in (None, "none")
        and f.get("acodec") not in (None, "none")
    ]
    if combined_any:
        best = max(combined_any, key=lambda f: f.get("height") or 0)
        return best.get("url", "")

    # 3. Fallback: video-only stream (browser will play without audio)
    video_only = [f for f in formats if f.get("vcodec") not in (None, "none")]
    if video_only:
        best = max(video_only, key=lambda f: f.get("height") or 0)
        return best.get("url", "")

    return ""
