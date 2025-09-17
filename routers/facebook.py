from fastapi import APIRouter, BackgroundTasks # 1. Import BackgroundTasks
from services.downloader_service import YTDLPService
from models.requests import FacebookDownloadRequest
import tempfile
import os

router = APIRouter()
downloader_service = YTDLPService()

@router.post("/facebook/download")
# 2. Add background_tasks to the function signature
async def download_facebook_video(request: FacebookDownloadRequest, background_tasks: BackgroundTasks):
    # Create a temporary file with a unique name
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_cookie_file:
        # Write the user-provided cookies to this file
        temp_cookie_file.write(request.cookies)
        cookie_file_path = temp_cookie_file.name
        
    custom_opts = {
        'cookiefile': cookie_file_path
    }

    try:
        # 3. Pass background_tasks to the download service
        result = downloader_service.download_video(
            url=request.url,
            background_tasks=background_tasks,
            custom_opts=custom_opts
        )
        return result
    finally:
        # Crucially, ensure the temporary cookie file is deleted after the operation
        if os.path.exists(cookie_file_path):
            os.remove(cookie_file_path)