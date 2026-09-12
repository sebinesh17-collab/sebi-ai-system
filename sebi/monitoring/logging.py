from __future__ import annotations

import logging
from pathlib import Path


def configure_logging(log_level: str = "INFO", log_path: str = "./logs/sebi.log") -> None:
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(path, encoding="utf-8"),
        ],
        force=True,
    )
