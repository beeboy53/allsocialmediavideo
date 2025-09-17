from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from services.downloader_service import YTDLPService
from models.requests import YouTubeDownloadRequest
import tempfile
import os

router = APIRouter()
downloader_service = YTDLPService()

@router.post("/youtube/download")
async def download_youtube_video(request: Request, yt_request: YouTubeDownloadRequest, background_tasks: BackgroundTasks):
    custom_opts = {}
    
    if yt_request.resolution:
        resolution_val = yt_request.resolution.replace('p', '')
        format_str = f'bestvideo[ext=mp4][height<={resolution_val}]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        custom_opts['format'] = format_str

    if yt_request.cookies:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_cookie_file:
            temp_cookie_file.write(yt_request.cookies)
            cookie_file_path = temp_cookie_file.name
        
        custom_opts['cookiefile'] = cookie_file_path

        try:
            result = downloader_service.download_video(
                url=yt_request.url,
                request=request,
                background_tasks=background_tasks,
                custom_opts=custom_opts
            )
            return result
        finally:
            if os.path.exists(cookie_file_path):
                os.remove(cookie_file_path)
    else:
        result = downloader_service.download_video(
            url=yt_request.url,
            request=request,
            background_tasks=background_tasks,
            custom_opts=custom_opts
        )
        return result
