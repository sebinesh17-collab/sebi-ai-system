from __future__ import annotations

from fastapi import APIRouter, Depends

from sebi.core.brain import SEBIBrain

from .utils import get_brain

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/status")
def get_status(brain: SEBIBrain = Depends(get_brain)) -> dict:
    return brain.system_status()


@router.post("/watch/scan")
def scan_watch_directory(brain: SEBIBrain = Depends(get_brain)) -> dict:
    return {"results": brain.run_watcher_once()}
