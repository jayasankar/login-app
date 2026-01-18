import logging
import json

# Configure logging with structured format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: Name of the logger (typically __name__ from the calling module)

    Returns:
        Logger instance configured with structured logging
    """
    return logging.getLogger(name)


def log_json(logger: logging.Logger, level: str, data: dict) -> None:
    """
    Log a structured JSON message at the specified level.

    Args:
        logger: Logger instance to use
        level: Logging level ('info', 'warning', 'error', 'debug')
        data: Dictionary containing the data to log
    """
    log_method = getattr(logger, level.lower())
    log_method(json.dumps(data))
