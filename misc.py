from datetime import datetime
from logger import logger


def timestamp():
    current_time = datetime.now()
    return current_time.strftime('%d/%m/%Y %H:%M')


def on_start():
    msg = f"Bot started at {timestamp()}"
    logger.info(msg)


def on_stop():
    msg = f"Bot stopped at {timestamp()}"
    logger.info(msg)