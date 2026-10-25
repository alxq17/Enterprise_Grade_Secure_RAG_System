import sys
from loguru import logger
from src.config.settings import settings

# Ensure UTF-8 output on Windows consoles to prevent UnicodeEncodeError with multilingual logs
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def setup_logging():
    """Config loguru logger for Enterprise."""
    logger.remove()
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    logger.add(sys.stdout, format=log_format, level=settings.LOG_LEVEL, colorize=True,)
    return logger

app_logger = setup_logging()