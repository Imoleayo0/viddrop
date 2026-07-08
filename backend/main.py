# ================================
# main.py - FastAPI app + routes
# ================================

import asyncio
import logging
import mimetypes
import traceback
from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, HttpUrl
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from cleaner import delete_file_after_send, purge_stale_files
from config import CORS_ORIGINS
from downloader import DownloadError, download_video
from security import SecurityError, limiter, validate_quality, validate_url

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
)
logger = logging.getLogger(__name__)


# Fix 1: replaced deprecated @app.on_event("startup") with lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("VidDrop API starting up...")
    asyncio.create_task(purge_stale_files())
    yield


app = FastAPI(
    title="VidDrop API",
    description="Video download backend powered by yt-dlp",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)


class DownloadRequest(BaseModel):
    url: HttpUrl
    platform: str = "auto"
    quality: str = "1080p"


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/download")
@limiter.limit("5/minute")
async def handle_download(
    request: Request,
    body: DownloadRequest,
    background_tasks: BackgroundTasks,
):
    url = str(body.url)
    quality = body.quality

    try:
        validate_url(url)
        validate_quality(quality)
    except SecurityError as exc:
        logger.warning(f"Security rejection: {exc} | url={url}")
        raise HTTPException(status_code=400, detail=str(exc))

    logger.info(
        "Download request - platform=%s quality=%s url=%s",
        body.platform,
        quality,
        url,
    )

    try:
        file_path, filename = await download_video(url, quality)
    except DownloadError as exc:
        logger.warning(f"Download failed: {exc}")
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.error(f"Unexpected error: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

    mime, _ = mimetypes.guess_type(filename)
    mime = mime or "application/octet-stream"

    # Fix 2: removed background= from FileResponse to avoid double cleanup
    background_tasks.add_task(delete_file_after_send, file_path)

    return FileResponse(
        path=file_path,
        media_type=mime,
        filename=filename,
    )


# Fix 3: guard against swallowing HTTPException and RateLimitExceeded
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, (HTTPException, RateLimitExceeded)):
        raise exc

    logger.error(f"Unhandled exception:\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )