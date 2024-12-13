# Argparse Interface: Logger
# Logger for the Argparse Interface.

# MARK: Imports
import logging

# MARK: Constants
LOGGER_NAME = "ArgparseInterface"

# MARK: Function
def getLogger(level: int, name: str = LOGGER_NAME) -> logging.Logger:
    """
    Gets a configured logger with the given name and log level.

    level: The logging level to use.
    name: Override the name of the logger to get.
    """
    # Logger setup
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Setup log handler
    logHandler = logging.StreamHandler()
    logHandler.setLevel(level)

    formatter = logging.Formatter("[%(levelname)s | %(asctime)s] %(message)s")
    logHandler.setFormatter(formatter)

    logger.addHandler(logHandler)

    return logger
