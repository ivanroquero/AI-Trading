import logging
from logging.handlers import RotatingFileHandler

def setup_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler("trading.log", maxBytes=5*1024*1024, backupCount=5)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logging.info("Logger initialized")