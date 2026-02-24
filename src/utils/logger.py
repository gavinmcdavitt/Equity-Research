import logging
from logging.handlers import TimedRotatingFileHandler
from src.config import config
import os

def setup_logging():
    log_dir = config['paths']['logs_dir']
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, config['logging']['file'])

    logger = logging.getLogger()
    logger.setLevel(getattr(logging, config['logging']['level']))

    # File handler with rotation
    file_handler = TimedRotatingFileHandler(
        log_file,
        when=config['logging']['rotate_when'],
        backupCount=config['logging']['rotate_backup_count']
    )
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)

    return logger

logger = setup_logging()