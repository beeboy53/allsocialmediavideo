# models/requests.py

from pydantic import BaseModel
from typing import Optional

class YouTubeDownloadRequest(BaseModel):
    url: str
    resolution: Optional[str] = None
    cookies: Optional[str] = None

class FacebookDownloadRequest(BaseModel):
    url: str
    cookies: str

class TikTokDownloadRequest(BaseModel):
    url: str

# ADD THIS NEW MODEL
class GenericDownloadRequest(BaseModel):

    url: str
