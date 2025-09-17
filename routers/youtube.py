# routers/youtube.py

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks # <-- Add BackgroundTasks
from services.downloader_service import YTDLPService
from models.requests import YouTubeDownloadRequest
import tempfile
import os

router = APIRouter()
downloader_service = YTDLPService()

#                              👇 Add background_tasks here
@router.post("/youtube/download")
async def download_youtube_video(request: YouTubeDownloadRequest, background_tasks: BackgroundTasks):
    custom_opts = {}
    
    if request.resolution:
        resolution_val = request.resolution.replace('p', '')
        format_str = f'bestvideo[ext=mp4][height<={resolution_val}]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        custom_opts['format'] = format_str

    if request.cookies:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_cookie_file:
            temp_cookie_file.write(request.cookies)
            cookie_file_path = temp_cookie_file.name
        
        custom_opts['cookiefile'] = cookie_file_path

        try:
            # 👇 Pass background_tasks to the service
            result = downloader_service.download_video(
                request.url,
                background_tasks=background_tasks,
                custom_opts=custom_opts
            )
            return result
        finally:
            if os.path.exists(cookie_file_path):
                os.remove(cookie_file_path)
    else:
        # 👇 Pass background_tasks to the service
        result = downloader_service.download_video(
            request.url,
            background_tasks=background_tasks,
            custom_opts=custom_opts
        )
        return result