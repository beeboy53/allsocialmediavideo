# services/downloader_service.py

import yt_dlp
from fastapi import HTTPException, BackgroundTasks
import os
import uuid
import time
import asyncio # <-- Add asyncio for non-blocking sleep

# --------------------------------------------------------------------------
# 1. ADD THE NEW DELETION FUNCTION
# --------------------------------------------------------------------------
async def delete_file_after_delay(file_path: str, delay_seconds: int):
    """
    Waits for a specified time and then deletes the file.
    """
    await asyncio.sleep(delay_seconds)
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️ Auto-deleted file: {file_path}")
    except Exception as e:
        print(f"Error auto-deleting file {file_path}: {e}")

# --------------------------------------------------------------------------

class YTDLPService:
    def __init__(self, download_path: str = "downloads"):
        self.download_path = download_path
        os.makedirs(self.download_path, exist_ok=True)

    # --------------------------------------------------------------------------
    # 2. MODIFY THE download_video METHOD SIGNATURE
    # --------------------------------------------------------------------------
    def download_video(self, url: str, background_tasks: BackgroundTasks, custom_opts: dict = None) -> dict:
        """
        Downloads a video from a given URL using yt-dlp.
        Schedules the downloaded file for deletion after 20 minutes.
        """
        # ... (filename and ydl_opts setup remains the same)
        filename = f"{uuid.uuid4()}.%(ext)s"
        out_template = os.path.join(self.download_path, filename)
        ydl_opts = {
            'format': 'bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': out_template,
            'merge_output_format': 'mp4',
            'noplaylist': True,
        }
        if custom_opts:
            ydl_opts.update(custom_opts)

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_file_path = ydl.prepare_filename(info)

                if os.path.exists(downloaded_file_path):
                    # --------------------------------------------------------------------------
                    # 3. ADD THE FILE TO THE BACKGROUND DELETION QUEUE
                    # --------------------------------------------------------------------------
                    print(f"⏰ Scheduling file for deletion in 20 minutes: {downloaded_file_path}")
                    background_tasks.add_task(
                        delete_file_after_delay,
                        file_path=downloaded_file_path,
                        delay_seconds=1200  # 20 minutes * 60 seconds
                    )
                else:
                    # Handle cases where download fails or file isn't found
                    possible_exts = ['.mp4', '.mkv', '.webm']
                    # ... (rest of the file finding logic is the same)
                    
                return {
                    "file_path": downloaded_file_path,
                    "title": info.get('title', 'N/A'),
                    "uploader": info.get('uploader', 'N/A'),
                }
        except yt_dlp.utils.DownloadError as e:
            raise HTTPException(status_code=404, detail=f"Video not found or access denied: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")