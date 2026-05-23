# SaveClips Downloader API v2.0

A FastAPI backend for downloading videos from YouTube, Facebook, TikTok, Instagram, Telegram, and generic URLs using yt-dlp.

---

## Quick Start (Local)

### 1. Prerequisites

- Python 3.11+
- `ffmpeg` installed and on your PATH (required for merging video+audio)
  - **Windows**: Download from https://ffmpeg.org/download.html → add `bin/` to PATH
  - **Linux/Mac**: `sudo apt install ffmpeg` or `brew install ffmpeg`

### 2. Clone / extract the project

```
saveclips-downloader/
└── download/           ← this is your working directory
    ├── main.py
    ├── .env
    ├── requirements.txt
    ├── cookies/
    │   ├── youtube.txt
    │   └── facebook.txt
    ├── core/
    ├── models/
    ├── routers/
    └── services/
```

### 3. Create a virtual environment

```bash
# From inside the download/ directory:
python -m venv venv

# Activate:
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment

Edit `.env`:
```
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
```
Get credentials from https://my.telegram.org → App configuration.

If you don't use Telegram, leave this as-is. The API will start normally but the `/telegram/download` endpoint will return 503.

### 6. (Optional) Add cookies for YouTube / Facebook

Cookies allow downloading age-restricted or private videos.

1. Install the **"Get cookies.txt LOCALLY"** browser extension
2. Log in to YouTube or Facebook
3. Click the extension → Export cookies
4. Paste the content into `cookies/youtube.txt` or `cookies/facebook.txt`

The files use Netscape cookie format:
```
# Netscape HTTP Cookie File
.youtube.com	TRUE	/	TRUE	1795099330	VISITOR_INFO1_LIVE	your_value
```

### 7. (Optional) Authorize Telegram

Only needed if you use the `/telegram/download` endpoint.

```bash
python encode_session.py
```

Follow the prompts. This creates `downloader_session.session` once. After that, the API connects automatically.

### 8. Run the API

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Open Swagger docs: http://localhost:8000/docs

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/health` | Health check |
| POST | `/youtube/download` | Download YouTube video |
| POST | `/facebook/download` | Download Facebook video |
| POST | `/tiktok/download` | Download TikTok video |
| POST | `/instagram/download` | Download Instagram video/Reel |
| GET | `/instagram/info?url=...` | Extract Instagram metadata |
| POST | `/telegram/download` | Download Telegram media |
| POST | `/generic/download` | Download from any yt-dlp URL |

---

## Example curl Requests

**YouTube (no resolution):**
```bash
curl -X POST http://localhost:8000/youtube/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

**YouTube (720p):**
```bash
curl -X POST http://localhost:8000/youtube/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "resolution": "720p"}'
```

**Facebook:**
```bash
curl -X POST http://localhost:8000/facebook/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.facebook.com/watch?v=123456789"}'
```

**TikTok:**
```bash
curl -X POST http://localhost:8000/tiktok/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.tiktok.com/@user/video/7123456789"}'
```

**Instagram Reel:**
```bash
curl -X POST http://localhost:8000/instagram/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.instagram.com/reel/ABC123/"}'
```

**Generic:**
```bash
curl -X POST http://localhost:8000/generic/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://vimeo.com/123456789"}'
```

---

## Production (Linux with Gunicorn)

```bash
gunicorn main:app \
  --worker-class uvicorn.workers.UvicornWorker \
  --workers 2 \
  --bind 0.0.0.0:8000 \
  --timeout 300
```

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `ERROR: Requested format is not available` | Try a lower resolution, or omit `resolution` field |
| `Only images are available` | The URL points to a photo post, not a video |
| `Sign in to confirm your age` | Add YouTube cookies to `cookies/youtube.txt` |
| `Telegram session is not authorized` | Run `python encode_session.py` first |
| `ffmpeg not found` | Install ffmpeg and add it to PATH |
| `Private video` | Add valid cookies for that platform |
