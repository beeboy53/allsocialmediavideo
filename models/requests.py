# models/requests.py

from pydantic import BaseModel
from typing import Optional

class YouTubeDownloadRequest(BaseModel):
    url: str
    cookies: Optional[str] = None # <-- resolution field removed

class FacebookDownloadRequest(BaseModel):
    url: str
    cookies: str

class TikTokDownloadRequest(BaseModel):
    url: str

class GenericDownloadRequest(BaseModel):
    url: str
