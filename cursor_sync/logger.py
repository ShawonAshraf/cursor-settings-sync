"""
Logger module for cursor-settings-sync.

Configures logging for the application.
"""

import sys
from loguru import logger
from .config import LOG_FILE_NAME, LOG_ROTATION_SIZE, LOG_RETENTION_DAYS


def setup_logging():
    """Set up logging configuration for the application."""
    # Remove default handler
    logger.remove()
    
    # Add console handler with colored formatting
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # Add file handler with rotation and retention
    logger.add(
        LOG_FILE_NAME,
        rotation=LOG_ROTATION_SIZE,
        retention=LOG_RETENTION_DAYS,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG"
    )
    
    return logger
