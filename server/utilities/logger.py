"""This module contains a rotating logger for game events."""
import logging
from os import path
from logging.handlers import RotatingFileHandler

LOG_DIRECTORY = './logs'
MAX_LOG_FILESIZE = 100000000  # 100000000 bytes = 10 MB


def create_logger(logger_name, fname='game.log'):
    """Create a logger.

    In any file, run this function to create a logger.

    The loglevel for game events is `game_event`.

    Regarding levels:

        DEBUG is 10, INFO is 20, WARNING is 30. GAME_EVENT is set to 35,
        because it should log game events even when warnings are turned
        off.

    Find out more about that here:
    https://docs.python.org/3/library/logging.html#logging-levels

    Example usage:

    ```
    log = create_logger(__name__)
    log.game_event('saluton mondo')
    ```
    """
    logging.GAME_EVENT_LEVEL_NUM = 35
    logging.addLevelName(logging.GAME_EVENT_LEVEL_NUM,
                         'GAME_EVENT')

    def game_event(self, message, *args, **kwargs):
        self._log(logging.GAME_EVENT_LEVEL_NUM, message, args, **kwargs)

    logging.Logger.game_event = game_event

    logfile = path.join(LOG_DIRECTORY, fname)
    print(f'setting logfile to {logfile}')

    logger = logging.getLogger(logger_name)
    # GAME_EVENT level is above warning
    logger.setLevel(logging.WARNING)

    # add a rotating handler
    handler = RotatingFileHandler(logfile,
                                  maxBytes=MAX_LOG_FILESIZE,
                                  backupCount=5)
    logger.addHandler(handler)
    return logger
