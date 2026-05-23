# models/requests.py
# Pydantic request models for all endpoints.

from pydantic import BaseModel, HttpUrl
from typing import Optional


class YouTubeDownloadRequest(BaseModel):
    url: str
    resolution: Optional[str] = None  # e.g. "720p", "1080p", "480p"

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "resolution": "720p",
            }
        }


class FacebookDownloadRequest(BaseModel):
    url: str  # Cookies are now loaded automatically from cookies/facebook.txt

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://www.facebook.com/watch?v=123456789",
            }
        }


class TikTokDownloadRequest(BaseModel):
    url: str

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://www.tiktok.com/@user/video/7123456789012345678",
            }
        }


class InstagramDownloadRequest(BaseModel):
    url: str

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://www.instagram.com/reel/ABC123/",
            }
        }


class TelegramDownloadRequest(BaseModel):
    url: str

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://t.me/channelname/123",
            }
        }


class GenericDownloadRequest(BaseModel):
    url: str

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://vimeo.com/123456789",
            }
        }
