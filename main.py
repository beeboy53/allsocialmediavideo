# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import youtube, facebook, tiktok, generic

app = FastAPI()

# --- CORS Middleware Configuration ---
origins = [
    "https://saveclips.download",
    "https://www.saveclips.download",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ------------------------------------

# Include all the remaining platform-specific routers
app.include_router(youtube.router, tags=["YouTube"])
app.include_router(facebook.router, tags=["Facebook"])
app.include_router(tiktok.router, tags=["TikTok"])
app.include_router(generic.router, tags=["Generic"])

@app.get("/")
async def root():
    return {"message": "Multi-platform video downloader API is running."}
