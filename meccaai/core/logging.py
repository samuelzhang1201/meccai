"""Structured logging configuration."""

import logging
import logging.config
from pathlib import Path

import yaml


def setup_logging(config_path: Path | None = None) -> None:
    """Setup structured logging from configuration file."""
    if config_path is None:
        config_path = Path("config/logging.yaml")

    if not config_path.exists():
        # Fallback to basic logging if config file doesn't exist
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        return

    # Ensure logs directory exists
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Load logging configuration
    with open(config_path) as f:
        config = yaml.safe_load(f)

    logging.config.dictConfig(config)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)
