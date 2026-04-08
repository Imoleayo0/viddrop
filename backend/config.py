# ================================
# config.py - App settings
# ================================

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

temp_dir_value = os.getenv("TEMP_DIR") or os.getenv("TMP_DIR") or "/tmp/viddrop"
TEMP_DIR = Path(temp_dir_value)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

FILE_TTL_SECONDS = int(os.getenv("FILE_TTL_SECONDS", 300))

CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5500,http://127.0.0.1:5500",
    ).split(",")
    if origin.strip()
]

MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 500 * 1024 * 1024))

# Maps frontend quality keys to yt-dlp format strings.
QUALITY_FORMATS: dict[str, str] = {
    "2160p": "bestvideo[height<=2160][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=2160]+bestaudio/best[height<=2160]/best",
    "1080p": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
    "720p": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best[height<=720]/best",
    "480p": "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=480]+bestaudio/best[height<=480]/best",
    "audio": "bestaudio[ext=m4a]/bestaudio",
}

DEFAULT_FORMAT = QUALITY_FORMATS["1080p"]
