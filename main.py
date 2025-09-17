from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

# Import the service instance from its new location
from core.dependencies import telegram_service
from routers import youtube, facebook, tiktok, telegram, generic

@asynccontextmanager
async def lifespan(app: FastAPI):
    # The lifespan manager uses the imported service
    await telegram_service.connect()
    yield
    await telegram_service.disconnect()

app = FastAPI(lifespan=lifespan)

# --- CORS Middleware Configuration ---
# This allows your frontend website to make requests to this API
origins = [
    "https://saveclips.download",
    "https://www.saveclips.download",
    # You might want to add localhost for local development
    # "http://localhost",
    "http://localhost:8080",
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
app.include_router(facebook.router, tags=["Facebook"])
app.include_router(tiktok.router, tags=["TikTok"])
app.include_router(telegram.router, tags=["Telegram"])
app.include_router(generic.router, tags=["Generic"])

@app.get("/")
async def root():
    return {"message": "Multi-platform video downloader API is running."}