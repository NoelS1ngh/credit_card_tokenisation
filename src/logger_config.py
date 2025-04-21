import logging
from colorlog import ColoredFormatter


def setup_logger(name=__name__):
    log_colours = {'INFO': 'blue', 'DEBUG': 'green', 'WARNING': 'light_yellow', 'ERROR': 'bold red'}

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        formatter = ColoredFormatter('%(log_color)s %(asctime)s - %(levelname)s]: %(message)s', log_colors=log_colours)
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
