import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict


class ColoredFormatter(logging.Formatter):
    """Formatter with colored output for different client types."""

    # Colors for different client types
    CLIENT_COLORS = {
        "user": "\033[32m",  # Green for user clients
        "bot": "\033[36m",  # Cyan for bot clients
        "system": "\033[35m"  # Purple for system messages
    }

    LEVEL_COLORS = {
        logging.DEBUG: "\033[37m",  # White
        logging.INFO: "\033[32m",  # Green
        logging.WARNING: "\033[33m",  # Yellow
        logging.ERROR: "\033[31m",  # Red
        logging.CRITICAL: "\033[41m"  # Red background
    }

    RESET = "\033[0m"

    def format(self, record):
        # Determine client type from logger name
        client_type = "system"
        if "_" in record.name:
            prefix = record.name.split("_")[0]
            if prefix in ["user", "bot"]:
                client_type = prefix

        # Add color for client type
        client_color = self.CLIENT_COLORS.get(client_type, "")
        level_color = self.LEVEL_COLORS.get(record.levelno, "")

        # Format the message
        record.msg = f"{client_color}[{record.name}]{self.RESET} {level_color}{record.msg}{self.RESET}"

        return super().format(record)


class LoggerFactory:
    _loggers: Dict[str, logging.Logger] = {}

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        if name in cls._loggers:
            return cls._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        if not logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(ColoredFormatter(
                "%(asctime)s - %(message)s",
                datefmt="%H:%M:%S"
            ))
            logger.addHandler(console_handler)

            # Rotating file handler
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)

            # Determine client type from logger name
            client_type = "system"
            if "_" in name:
                client_type = name.split("_")[0]

            # Create a separate file for each client type
            file_handler = RotatingFileHandler(
                log_dir / f"{client_type}.log",
                maxBytes=2 * 1024 * 1024,  # 2MB
                backupCount=3,
                encoding="utf-8"
            )
            file_handler.setFormatter(logging.Formatter(
                "%(asctime)s - [%(name)s] - %(levelname)s - %(message)s"
            ))
            logger.addHandler(file_handler)

        cls._loggers[name] = logger
        return logger


def get_logger(name: str) -> logging.Logger:
    return LoggerFactory.get_logger(name)
