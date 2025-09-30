# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
from routers import youtube, facebook, tiktok, generic

# Create the FastAPI app instance first
app = FastAPI()

# --- CORS Middleware Configuration ---
# This needs to be near the top to apply to all routes
origins = [
    "https://saveclips.download",
    "https://www.saveclips.download",
    "http://saveclips.download",
    "http://www.saveclips.download",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- New File Serving Endpoint ---
# This replaces the old app.mount() and correctly handles CORS
@app.get("/downloads/{file_name}")
async def get_downloaded_file(file_name: str):
    file_path = os.path.join("downloads", file_name)
    
    # Security check to prevent accessing files outside the 'downloads' folder
    if os.path.exists(file_path) and ".." not in file_name:
        return FileResponse(path=file_path, media_type='application/octet-stream', filename=file_name)
    
    return {"error": "File not found"}, 404

# --- Include all the platform-specific routers ---
app.include_router(youtube.router, tags=["YouTube"])
app.include_router(facebook.router, tags=["Facebook"])
app.include_router(tiktok.router, tags=["TikTok"])
app.include_router(generic.router, tags=["Generic"])

# --- Root Endpoint ---
@app.get("/")
async def root():
    return {"message": "Multi-platform video downloader API is running."}

# Note: The 'app.mount("/downloads", StaticFiles(directory="downloads"))' line 
# has been removed because the new endpoint above handles this functionality now.

