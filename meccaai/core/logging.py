"""Backward compatibility logging for console output."""

import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """Get a simple console logger for backward compatibility."""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # Add console handler if not already present
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    
    return logger