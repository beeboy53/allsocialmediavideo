# services/downloader_service.py
# Core yt-dlp wrapper used by all platform routers.

import yt_dlp
from fastapi import HTTPException, BackgroundTasks
import os
import uuid
import asyncio
import logging

logger = logging.getLogger(__name__)

# Common browser User-Agent to avoid bot detection
_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/136.0.0.0 Safari/537.36"
)

# --------------------------------------------------------------------------
# In-memory file registry: unique_id -> absolute file path
# --------------------------------------------------------------------------

_file_registry: dict[str, str] = {}


def get_registered_path(uid: str) -> str | None:
    """Returns the absolute file path for a given unique_id, or None if not found."""
    return _file_registry.get(uid)


# --------------------------------------------------------------------------
# Background auto-deletion
# --------------------------------------------------------------------------

async def delete_file_after_delay(file_path: str, delay_seconds: int = 1200):
    """Deletes a downloaded file after a delay (default 20 min)."""
    await asyncio.sleep(delay_seconds)
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Auto-deleted: {file_path}")
        # Remove from registry
        to_remove = [k for k, v in _file_registry.items() if v == file_path]
        for k in to_remove:
            del _file_registry[k]
    except Exception as e:
        logger.warning(f"Could not auto-delete {file_path}: {e}")


# --------------------------------------------------------------------------
# Service
# --------------------------------------------------------------------------

class YTDLPService:

    def __init__(self, download_path: str = "downloads"):
        self.download_path = download_path
        os.makedirs(self.download_path, exist_ok=True)

    def _base_opts(self) -> dict:
        """Returns sensible yt-dlp defaults shared across all platforms."""
        return {
            "outtmpl": "",           # set per-call
            "merge_output_format": "mp4",
            "noplaylist": True,
            "quiet": False,
            "no_warnings": False,
            "http_headers": {"User-Agent": _USER_AGENT},
            # Retry logic
            "retries": 5,
            "fragment_retries": 5,
            "file_access_retries": 3,
        }

    def download_video(
        self,
        url: str,
        background_tasks: BackgroundTasks,
        custom_opts: dict = None,
    ) -> dict:
        """
        Downloads a video from the given URL.
        custom_opts overrides/extends the base yt-dlp options.
        Schedules auto-deletion of the file after 20 minutes.
        """
        unique_id = str(uuid.uuid4())
        out_template = os.path.join(self.download_path, f"{unique_id}.%(ext)s")

        opts = self._base_opts()
        opts["outtmpl"] = out_template

        # Default format if caller doesn't supply one
        opts["format"] = (
            "bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]"
            "/bestvideo[height<=1080]+bestaudio"
            "/best[ext=mp4]"
            "/best"
        )

        if custom_opts:
            opts.update(custom_opts)

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)

                # Resolve actual output path -----------------------------------------------
                # Priority 1: yt-dlp's own requested_downloads record
                downloaded_path = None
                requested = info.get("requested_downloads") or []
                if requested and requested[0].get("filepath"):
                    downloaded_path = requested[0]["filepath"]

                # Priority 2: scan downloads/ for our unique_id prefix
                if not downloaded_path or not os.path.exists(downloaded_path):
                    for fname in os.listdir(self.download_path):
                        if fname.startswith(unique_id):
                            downloaded_path = os.path.join(self.download_path, fname)
                            break

                if not downloaded_path or not os.path.exists(downloaded_path):
                    raise HTTPException(
                        status_code=500,
                        detail="Download completed but output file could not be located.",
                    )

                # Register file so /file/{uid} can serve it
                _file_registry[unique_id] = downloaded_path

                # Schedule cleanup
                background_tasks.add_task(
                    delete_file_after_delay,
                    file_path=downloaded_path,
                    delay_seconds=1200,
                )

                logger.info(f"Downloaded: {downloaded_path}")
                return {
                    "download_url": f"/file/{unique_id}",
                    "title": info.get("title", "Unknown"),
                    "uploader": info.get("uploader") or info.get("channel") or "Unknown",
                    "duration": info.get("duration"),
                    "thumbnail": info.get("thumbnail"),
                }

        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            logger.error(f"yt-dlp DownloadError for {url}: {error_msg}")

            if "Requested format is not available" in error_msg:
                raise HTTPException(
                    status_code=422,
                    detail=(
                        "Requested format/resolution is not available for this video. "
                        "Try a lower resolution or omit the resolution field."
                    ),
                )
            if "Private video" in error_msg or "Sign in" in error_msg:
                raise HTTPException(
                    status_code=403,
                    detail="This video is private or requires authentication. Add valid cookies.",
                )
            raise HTTPException(
                status_code=400,
                detail=f"Download failed: {error_msg}",
            )

        except HTTPException:
            raise

        except Exception as e:
            logger.exception(f"Unexpected error downloading {url}")
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

    def extract_info(self, url: str, extra_opts: dict = None) -> dict:
        """
        Extracts video metadata without downloading.
        Used by the Instagram info endpoint.
        """
        opts = self._base_opts()
        opts.update({
            "skip_download": True,
            "quiet": True,
            "no_warnings": True,
        })
        if extra_opts:
            opts.update(extra_opts)

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
        except yt_dlp.utils.DownloadError as e:
            raise HTTPException(status_code=400, detail=f"Could not fetch info: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
