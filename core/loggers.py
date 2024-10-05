import logging
from colorlog import ColoredFormatter



def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with the given name and level.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(log_color)s%(message)s',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

logger = setup_logger("GRC_logger")