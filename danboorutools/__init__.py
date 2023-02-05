import os
import sys

from dotenv import load_dotenv
from loguru import logger

load_dotenv()

logger = logger.opt(colors=True)
logger.remove()
logger.add(sys.stderr, level=os.environ.get("LOGURU_LEVEL", "INFO"))
