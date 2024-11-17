# src/catalyst/core/logger.py
import logging
import sys
from pathlib import Path
from typing import Optional
from rich.logging import RichHandler
from rich.console import Console
from rich.traceback import install

# Install rich traceback handler
install()

class CatalystLogger:
    """Custom logger for Catalyst with rich formatting"""
    
    def __init__(
        self,
        name: str,
        level: str = "INFO",
        log_file: Optional[Path] = None
    ):
        self.console = Console()
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level.upper())

        # Remove existing handlers
        self.logger.handlers = []

        # Console handler with rich formatting
        console_handler = RichHandler(
            console=self.console,
            show_time=True,
            show_path=True,
            rich_tracebacks=True
        )
        
        # Format for console output
        console_format = logging.Formatter(
            "%(message)s",
            datefmt="[%X]"
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)

        # File handler if log_file is specified
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_format = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(file_format)
            self.logger.addHandler(file_handler)

    def get_logger(self) -> logging.Logger:
        """Get the configured logger"""
        return self.logger

# Global logger instance
def get_logger(
    name: str,
    level: str = "INFO",
    log_file: Optional[Path] = None
) -> logging.Logger:
    """Get a configured logger instance"""
    return CatalystLogger(name, level, log_file).get_logger()

