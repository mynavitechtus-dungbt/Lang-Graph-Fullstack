"""Logging setup — log file path is supplied by the caller."""

import logging
from pathlib import Path


def setup_logging(
    log_file: str | Path = "app.log",
    *,
    level: int = logging.INFO,
    logger_name: str | None = None,
) -> logging.Logger:
    """
    Configure a logger that writes to a file at the given path.

    Args:
        log_file: Path to the log file (str or Path).
        level: Log level (default INFO).
        logger_name: Logger name (defaults to the calling module's __name__).

    Returns:
        The configured logger.
    """
    log_path = (Path("./logs") / log_file).resolve()
    logger = logging.getLogger(logger_name or __name__)
    logger.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
