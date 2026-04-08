# ================================
# cleaner.py — Temp file cleanup
# ================================

import asyncio
import shutil
import logging
from pathlib import Path

from config import TEMP_DIR, FILE_TTL_SECONDS

logger = logging.getLogger(__name__)


async def delete_file_after_send(path: Path) -> None:
    """
    Delete a file (and its parent job folder) immediately after
    it has been sent to the client.
    Called as a background task by FastAPI.
    """
    try:
        if path.exists():
            path.unlink()
            logger.info(f"[cleaner] Deleted file: {path}")

        # Remove the empty job subfolder
        parent = path.parent
        if parent != TEMP_DIR and parent.exists():
            shutil.rmtree(parent, ignore_errors=True)
            logger.info(f"[cleaner] Removed job dir: {parent}")

    except Exception as e:
        logger.warning(f"[cleaner] Failed to delete {path}: {e}")


async def purge_stale_files() -> None:
    """
    Background loop — purges any files older than FILE_TTL_SECONDS.
    Catches cases where delete_file_after_send didn't run
    (e.g. client disconnected mid-download).
    """
    import time

    while True:
        await asyncio.sleep(60)  # check every minute
        now = time.time()

        for job_dir in TEMP_DIR.iterdir():
            if not job_dir.is_dir():
                continue
            try:
                age = now - job_dir.stat().st_mtime
                if age > FILE_TTL_SECONDS:
                    shutil.rmtree(job_dir, ignore_errors=True)
                    logger.info(f"[cleaner] Purged stale job: {job_dir}")
            except Exception as e:
                logger.warning(f"[cleaner] Error checking {job_dir}: {e}")
