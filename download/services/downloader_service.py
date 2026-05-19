# services/downloader_service.py

import yt_dlp
from fastapi import HTTPException, BackgroundTasks
import os
import uuid
import asyncio


# --------------------------------------------------------------------------
# Background deletion helper
# --------------------------------------------------------------------------
async def delete_file_after_delay(file_path: str, delay_seconds: int):
    await asyncio.sleep(delay_seconds)
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️  Auto-deleted file: {file_path}")
    except Exception as e:
        print(f"Error auto-deleting file {file_path}: {e}")


# --------------------------------------------------------------------------
# Main service
# --------------------------------------------------------------------------
class YTDLPService:

    def __init__(self, download_path: str = "downloads"):
        self.download_path = download_path
        os.makedirs(self.download_path, exist_ok=True)

    def download_video(
        self,
        url: str,
        background_tasks: BackgroundTasks,
        custom_opts: dict = None,
    ) -> dict:
        """
        Downloads a video from the given URL using yt-dlp.
        Schedules the downloaded file for auto-deletion after 20 minutes.
        """
        unique_id = str(uuid.uuid4())
        out_template = os.path.join(self.download_path, f"{unique_id}.%(ext)s")

        ydl_opts = {
            "format": "bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "outtmpl": out_template,
            "merge_output_format": "mp4",
            "noplaylist": True,
        }

        if custom_opts:
            ydl_opts.update(custom_opts)

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)

                # ------------------------------------------------------------------
                # FIX: resolve the actual downloaded file path correctly.
                # ydl.prepare_filename() returns the *template* path which still
                # contains %(ext)s or wrong extension before merging.
                # The reliable source is info["requested_downloads"][0]["filepath"].
                # Fallback: scan downloads folder for our unique_id prefix.
                # ------------------------------------------------------------------
                downloaded_file_path = None

                requested = info.get("requested_downloads") or []
                if requested and requested[0].get("filepath"):
                    downloaded_file_path = requested[0]["filepath"]

                if not downloaded_file_path or not os.path.exists(downloaded_file_path):
                    for fname in os.listdir(self.download_path):
                        if fname.startswith(unique_id):
                            downloaded_file_path = os.path.join(self.download_path, fname)
                            break

                if not downloaded_file_path or not os.path.exists(downloaded_file_path):
                    raise HTTPException(
                        status_code=500,
                        detail="Download appeared to succeed but the output file could not be located.",
                    )

                print(f"⏰ Scheduling deletion in 20 min: {downloaded_file_path}")
                background_tasks.add_task(
                    delete_file_after_delay,
                    file_path=downloaded_file_path,
                    delay_seconds=1200,
                )

                return {
                    "file_path": downloaded_file_path,
                    "title": info.get("title", "N/A"),
                    "uploader": info.get("uploader", "N/A"),
                }

        except yt_dlp.utils.DownloadError as e:
            raise HTTPException(status_code=404, detail=f"Video not found or access denied: {str(e)}")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")

    def extract_info(self, url: str) -> dict:
        """
        Extracts video/media metadata without downloading.
        Used by the Instagram info endpoint.
        """
        ydl_opts = {
            "quiet": True,
            "noplaylist": False,
            "extract_flat": False,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)
        except yt_dlp.utils.DownloadError as e:
            raise HTTPException(status_code=404, detail=f"Could not fetch media info: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")
