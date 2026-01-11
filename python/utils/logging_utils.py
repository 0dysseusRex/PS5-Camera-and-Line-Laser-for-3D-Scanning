"""logging_utils.py

Central logging configuration.
"""
from __future__ import annotations

import logging


def configure_logging(level: int = logging.INFO) -> None:
    fmt = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    logging.basicConfig(level=level, format=fmt)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
