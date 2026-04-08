# ================================
# downloader.py - yt-dlp wrapper
# ================================

import asyncio
import uuid
from pathlib import Path
from typing import Tuple

import yt_dlp

from config import DEFAULT_FORMAT, MAX_FILE_SIZE, QUALITY_FORMATS, TEMP_DIR


class DownloadError(Exception):
    """Raised when yt-dlp fails to download a video."""


def _build_ydl_opts(fmt: str, out_path: Path, is_audio: bool) -> dict:
    opts = {
        "format": fmt,
        "outtmpl": str(out_path / "%(title)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "max_filesize": MAX_FILE_SIZE,
    }

    if is_audio:
        opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ]

    return opts


def _find_downloaded_file(directory: Path) -> Path:
    files = list(directory.iterdir())
    if not files:
        raise DownloadError("Download completed but no file was found.")
    return files[0]


async def download_video(url: str, quality: str) -> Tuple[Path, str]:
    is_audio = quality == "audio"
    fmt = QUALITY_FORMATS.get(quality, DEFAULT_FORMAT)

    job_dir = TEMP_DIR / str(uuid.uuid4())
    job_dir.mkdir(parents=True, exist_ok=True)

    opts = _build_ydl_opts(fmt, job_dir, is_audio)

    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(None, _run_ydl, url, opts)
    except yt_dlp.utils.DownloadError as exc:
        raise DownloadError(str(exc)) from exc

    file_path = _find_downloaded_file(job_dir)
    return file_path, file_path.name


def _run_ydl(url: str, opts: dict) -> None:
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
