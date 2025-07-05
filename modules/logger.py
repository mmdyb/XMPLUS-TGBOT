from loguru import logger
import sys

from .warna import *


# journal logger
logger.remove()
logger.add(
    sink=sys.stdout,
    format=(
        "[<white>{time:YYYY-MM-DD HH:mm:ss}</white>] | "
        "<level>{level:^7}</level> | "
        "<cyan>{name}</cyan>:<cyan><b>{line}</b></cyan> - "
        "<level>{message}</level>"
    ),
    colorize=True,
    backtrace=True,
    diagnose=True,
)
logger.add("./logs/file_{time}.log", rotation="10 MB", retention="7 days", compression="zip")
log = logger.opt(colors=True)