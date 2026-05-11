import logging
import os
import sys
from logging.handlers import RotatingFileHandler

# Define log directory in the backend root
LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../logs'))
os.makedirs(LOG_DIR, exist_ok=True)

# Define log files
ACTIVITY_LOG_FILE = os.path.join(LOG_DIR, "activity.log")
ERROR_LOG_FILE = os.path.join(LOG_DIR, "error.log")

# Define formatter for detailed logs
formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Avoid duplicate handlers
    if not logger.handlers:
        # 1. Console Handler (INFO level)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        # 2. Activity Log Handler (INFO level - logs everything)
        activity_handler = RotatingFileHandler(
            ACTIVITY_LOG_FILE, maxBytes=5*1024*1024, backupCount=3
        )
        activity_handler.setLevel(logging.INFO)
        activity_handler.setFormatter(formatter)

        # 3. Error Log Handler (ERROR level - logs only exceptions/errors)
        error_handler = RotatingFileHandler(
            ERROR_LOG_FILE, maxBytes=5*1024*1024, backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(activity_handler)
        logger.addHandler(error_handler)

    return logger
