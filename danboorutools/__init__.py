from dotenv import load_dotenv
from loguru import logger

load_dotenv()
logger = logger.opt(colors=True)
