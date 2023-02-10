import os
import sys

from dotenv import load_dotenv
from loguru import logger

load_dotenv()

logger = logger.opt(colors=True)
logger.remove()

logger_level = os.environ.get("LOGURU_LEVEL") or os.environ.get("LOG_LEVEL") or "INFO"
debug = os.environ.get("DEBUG") in ["TRUE", "1"]
logger_level = "DEBUG" if debug else logger_level

logger.add(sys.stderr, level=logger_level)
