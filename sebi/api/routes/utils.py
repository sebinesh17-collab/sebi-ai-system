from __future__ import annotations

from functools import lru_cache

from config.settings import get_settings
from sebi.core.brain import SEBIBrain


@lru_cache()
def get_brain() -> SEBIBrain:
    return SEBIBrain(get_settings())
