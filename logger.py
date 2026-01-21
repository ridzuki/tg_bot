import logging
import os
from logging.handlers import TimedRotatingFileHandler
from typing import Optional, Dict, Any

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOGGER_NAME = "aiogram_bot"
LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | %(name)s | "
    "feature=%(feature)s | user=%(user_id)s | req=%(request_id)s | "
    "[%(module)s.%(funcName)s:%(lineno)d] %(message)s"
)
LOG_DATEFMT = "%Y-%m-%d %H:%M:%S"
LOG_LEVEL = logging.INFO

class _ContextDefaultsFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "feature"):
            record.feature = "-"
        if not hasattr(record, "user_id"):
            record.user_id = "-"
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return True

_base_logger = logging.getLogger(LOGGER_NAME)
_base_logger.setLevel(LOG_LEVEL)

if not _base_logger.handlers:
    file_handler = TimedRotatingFileHandler(
        filename=os.path.join(LOG_DIR, "bot.log"),
        when="midnight",
        interval=1,
        backupCount=14,
        encoding="utf-8",
        utc=False,
    )
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=LOG_DATEFMT))
    file_handler.addFilter(_ContextDefaultsFilter())

    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=LOG_DATEFMT))
    console_handler.addFilter(_ContextDefaultsFilter())

    _base_logger.addHandler(file_handler)
    _base_logger.addHandler(console_handler)

class _FeatureAdapter(logging.LoggerAdapter):
    def process(self, msg: str, kwargs: Dict[str, Any]):
        extra = kwargs.setdefault("extra", {})
        extra.setdefault("feature", self.extra.get("feature", "-"))
        return msg, kwargs


def get_logger(feature: Optional[str] = None) -> logging.Logger:
    return _FeatureAdapter(_base_logger, {"feature": feature or "-"})

logger = get_logger()