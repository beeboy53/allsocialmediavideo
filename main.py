# main.py
# SaveClips Video Downloader API
# Supports: YouTube, Facebook, TikTok, Instagram, Telegram, Generic

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import youtube, facebook, tiktok, generic, instagram, telegram

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
