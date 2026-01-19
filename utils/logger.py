"""
Logging yapılandırması
"""
import sys
from pathlib import Path
from loguru import logger as loguru_logger

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import settings


# Loguru konfigürasyonu
loguru_logger.remove()  # Varsayılan handler'ı kaldır

# Console logging
loguru_logger.add(
    sys.stderr,
    format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.log_level
)

# File logging
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

loguru_logger.add(
    str(log_dir / "app.log"),
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="INFO",
    rotation="500 MB",
    retention="10 days"
)

logger = loguru_logger
