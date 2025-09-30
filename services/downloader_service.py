import yt_dlp
from fastapi import HTTPException, BackgroundTasks, Request
import os
import uuid
import asyncio

async def delete_file_after_delay(file_path: str, delay_seconds: int):
    await asyncio.sleep(delay_seconds)
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️ Auto-deleted file: {file_path}")
    except Exception as e:
        print(f"Error auto-deleting file {file_path}: {e}")

class YTDLPService:
    def __init__(self, download_path: str = "downloads"):
        self.download_path = download_path
        os.makedirs(self.download_path, exist_ok=True)
        
    def download_video(self, url: str, request: Request, background_tasks: BackgroundTasks, custom_opts: dict = None) -> dict:
        filename = f"{uuid.uuid4()}.%(ext)s"
        out_template = os.path.join(self.download_path, filename)
        
        ydl_opts = {
    'format': 'best[ext=mp4]/best', # <-- Find the best pre-merged MP4 file
    'outtmpl': out_template,
    # 'merge_output_format' is no longer needed since we are not merging
    'noplaylist': True,
}
        if custom_opts: 
            ydl_opts.update(custom_opts)

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_file_path = ydl.prepare_filename(info)

                if os.path.exists(downloaded_file_path):
                    print(f"⏰ Scheduling file for deletion in 20 minutes: {downloaded_file_path}")
                    background_tasks.add_task(delete_file_after_delay, file_path=downloaded_file_path, delay_seconds=1200)
                    
                    file_name_only = os.path.basename(downloaded_file_path)
                    download_url = f"{str(request.base_url).rstrip('/')}/download/{file_name_only}"
                    
                    return {
                        "title": info.get('title', 'N/A'),
                        "thumbnail": info.get('thumbnail', None),
                        "download_url": download_url
                    }
                else:
                    raise HTTPException(status_code=500, detail="Download completed but the file could not be found on the server.")
                
        except Exception as e:
            error_message = str(e)
            if 'DownloadError' in str(type(e)) or 'yt-dlp' in error_message:
                 raise HTTPException(status_code=404, detail=f"Video not found or access denied: {error_message}")
            raise HTTPException(status_code=500, detail=f"An internal error occurred: {error_message}")

