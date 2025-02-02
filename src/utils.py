import logging
from collections.abc import Sequence
from pathlib import Path
from typing import TypeAlias


TimeframeList: TypeAlias = list[tuple[int, int]]


def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def validate_timeframes(timeframes: Sequence[int], duration: int) -> TimeframeList:
    return [(i, t) for i, t in enumerate(timeframes) if 0 <= t <= duration]


def ensure_output_path(path: str | Path) -> Path:
    output_path = Path(path)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def clean_failed_output(filepath: str | Path) -> None:
    path = Path(filepath)
    path.unlink(missing_ok=True)


def parse_timestamp(timestamp: str) -> int:
    """Convert h:m:s format to seconds"""
    try:
        match timestamp.split(":"):
            case [s]:
                return int(s)
            case [m, s]:
                return int(m) * 60 + int(s)
            case [h, m, s]:
                return int(h) * 3600 + int(m) * 60 + int(s)
            case _:
                raise ValueError
    except ValueError:
        raise ValueError(
            f"Invalid timestamp format: {timestamp}. Use h:m:s, m:s, or s"
        ) from None
