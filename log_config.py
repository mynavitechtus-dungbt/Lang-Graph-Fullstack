"""Cấu hình logging — tên file log được truyền từ bên ngoài."""

import logging
from pathlib import Path


def setup_logging(
    log_file: str | Path,
    *,
    level: int = logging.INFO,
    logger_name: str | None = None,
) -> logging.Logger:
    """
    Thiết lập logger ghi ra file với tên file được truyền vào.

    Args:
        log_file: Đường dẫn file log (string hoặc Path).
        level: Mức log (mặc định INFO).
        logger_name: Tên logger (mặc định __name__ của module gọi).

    Returns:
        Logger đã được cấu hình.
    """
    log_path = Path(log_file).resolve()
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
