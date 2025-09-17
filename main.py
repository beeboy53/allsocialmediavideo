from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse # <-- Import FileResponse
from routers import youtube, facebook, tiktok, generic
import os

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

# Include all the platform-specific routers
app.include_router(youtube.router, tags=["YouTube"])
# ... (include your other routers)

# --- NEW: Proper Download Endpoint ---
@app.get("/download/{filename}")
async def download_file(filename: str):
    """
    Serves a downloaded file and forces the browser to download it.
    """
    file_path = os.path.join("downloads", filename)
    if os.path.exists(file_path):
        return FileResponse(
            path=file_path,
            media_type='application/octet-stream',
            filename=filename
        )
    return {"error": "File not found."}
# ------------------------------------

@app.get("/")
async def root():
    return {"message": "Multi-platform video downloader API is running."}
