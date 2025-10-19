from loguru import logger
import sys

logger.remove()
logger.add(sys.stdout, level="INFO", backtrace=True, diagnose=False, enqueue=True,
           format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {name}:{function}:{line} | {message}")