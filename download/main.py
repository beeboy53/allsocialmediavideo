from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import youtube, facebook, tiktok, generic, instagram

app = FastAPI()

# --- CORS Middleware Configuration ---
origins = [
    "https://saveclips.download",
    "https://www.saveclips.download",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(youtube.router, tags=["YouTube"])
app.include_router(facebook.router, tags=["Facebook"])
app.include_router(tiktok.router, tags=["TikTok"])
app.include_router(generic.router, tags=["Generic"])
app.include_router(instagram.router, tags=["Instagram"])

# Root route
@app.get("/")
async def root():
    return {
        "message": "SaveClips multi-platform downloader API is running."
    }