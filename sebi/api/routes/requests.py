from __future__ import annotations

from fastapi import APIRouter, Depends

from sebi.core.brain import SEBIBrain
from sebi.core.models import IngestionRequest, ProcessRequest, ProcessResponse

from .utils import get_brain

router = APIRouter(tags=["requests"])


@router.post("/process", response_model=ProcessResponse)
def process_request(
    payload: ProcessRequest,
    brain: SEBIBrain = Depends(get_brain),
) -> ProcessResponse:
    return brain.process(payload)


@router.post("/ingest")
def ingest_file(
    payload: IngestionRequest,
    brain: SEBIBrain = Depends(get_brain),
) -> dict:
    return brain.ingest_path(payload.path)
