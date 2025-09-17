from fastapi import APIRouter, BackgroundTasks, Request
from services.downloader_service import YTDLPService
from models.requests import FacebookDownloadRequest
import tempfile
import os

router = APIRouter()
downloader_service = YTDLPService()

@router.post("/facebook/download")
async def download_facebook_video(request: Request, fb_request: FacebookDownloadRequest, background_tasks: BackgroundTasks):
    # Create a temporary file with a unique name
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_cookie_file:
        # Write the user-provided cookies to this file
        temp_cookie_file.write(fb_request.cookies)
        cookie_file_path = temp_cookie_file.name
        
    custom_opts = {
        'cookiefile': cookie_file_path
    }

    try:
        # Call the download service with the path to the cookie file
        result = downloader_service.download_video(
            url=fb_request.url,
            request=request,
            background_tasks=background_tasks,
            custom_opts=custom_opts
        )
        return result
    finally:
        # Crucially, ensure the temporary cookie file is deleted after the operation
        if os.path.exists(cookie_file_path):
            os.remove(cookie_file_path)
