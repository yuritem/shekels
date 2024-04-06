import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from bot.config import Settings


def setup_logging(
        config: Settings,
        logging_level_sqlalchemy: int = logging.WARNING,
        logging_level_root: int = logging.INFO
):
    """
    :param config: pydantic configuration object
    :param logging_level_sqlalchemy: logging level for sqlalchemy. Note: echo=True, echo="debug" will still log to stdout
    :param logging_level_root: logging level for the whole application
    :return:
    """

    if not os.path.exists(config.LOG_DIRECTORY):
        os.makedirs(config.LOG_DIRECTORY)

    log_filename = config.LOG_FILENAME
    if not log_filename.endswith('.log'):
        log_filename = f"{log_filename}.log"

    logging.getLogger('sqlalchemy').setLevel(logging_level_sqlalchemy)

    logger = logging.getLogger()
    logger.setLevel(logging_level_root)

    formatter = logging.Formatter(
        fmt="%(asctime)s.%(msecs)03d | %(name)s | %(funcName)s | %(levelname)s | %(message)s",
        datefmt="%Y.%m.%d %H:%M:%S"
    )

    file_handler = RotatingFileHandler(
        filename=os.path.join(config.LOG_DIRECTORY, log_filename),
        maxBytes=config.LOG_MAXBYTES,
        backupCount=config.LOG_BACKUPS,
        delay=True,
        encoding='utf-8'
    )
    stream_handler = logging.StreamHandler(stream=sys.stderr)

    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
