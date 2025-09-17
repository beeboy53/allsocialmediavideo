# routers/generic.py

from fastapi import APIRouter, BackgroundTasks, Request # <-- Import Request
from services.downloader_service import YTDLPService
from models.requests import GenericDownloadRequest

router = APIRouter()
downloader_service = YTDLPService()

@router.post("/generic/download")
                                             # 👇 Add request: Request here
async def download_generic_video(request: Request, generic_req: GenericDownloadRequest, background_tasks: BackgroundTasks):
    result = downloader_service.download_video(
        url=generic_req.url,
        request=request, # <-- Pass the request object
        background_tasks=background_tasks
    )
    return result
