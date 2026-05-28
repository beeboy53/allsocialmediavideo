# main.py
# SaveClips Video Downloader API
# Supports: YouTube, Facebook, TikTok, Instagram, Telegram, Generic

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os

from routers import youtube, facebook, tiktok, generic, instagram, telegram
from services.downloader_service import get_registered_path

app = FastAPI(
    title="SaveClips Downloader API",
    description="Multi-platform video downloader using yt-dlp",
    version="2.0.0",
)

# CORS - update origins to match your frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://saveclips.download",
        "https://www.saveclips.download",
        "http://localhost:8080",
        "http://localhost:3000",
        "*",  # Remove in production; use explicit origins above
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
app.include_router(youtube.router, tags=["YouTube"])
app.include_router(facebook.router, tags=["Facebook"])
app.include_router(tiktok.router, tags=["TikTok"])
app.include_router(generic.router, tags=["Generic"])
app.include_router(instagram.router, tags=["Instagram"])
app.include_router(telegram.router, tags=["Telegram"])


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "SaveClips API is running."}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}


@app.get("/file/{uid}", tags=["Download"])
async def serve_file(uid: str):
    """
    Serves a previously downloaded video file by its unique ID.
    The download_url returned by all download endpoints points here.
    Files are automatically deleted after 20 minutes.
    """
    path = get_registered_path(uid)
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found or expired.")
    filename = os.path.basename(path)
    return FileResponse(
        path=path,
        media_type="video/mp4",
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
