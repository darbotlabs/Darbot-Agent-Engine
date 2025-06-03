# logging_config.py
"""
Centralized logging configuration for consistent logging across the application
Thought into existence by Darbot
"""
import logging
import logging.config
import os
import sys
from typing import Dict, Any


def get_log_level() -> int:
    """Get the log level from environment variable or default to INFO"""
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    return getattr(logging, level_name, logging.INFO)


def setup_logging(
    log_level: int = None,
    enable_azure_logging: bool = True,
    enable_file_logging: bool = False,
    log_file_path: str = None
) -> None:
    """
    Set up centralized logging configuration
    
    Args:
        log_level: Logging level (defaults to LOG_LEVEL env var or INFO)
        enable_azure_logging: Whether to configure Azure monitor logging
        enable_file_logging: Whether to enable file logging
        log_file_path: Path for log file if file logging is enabled
    """
    
    if log_level is None:
        log_level = get_log_level()
    
    # Base logging configuration
    config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "detailed": {
                "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(funcName)s(): %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "json": {
                "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s", "module": "%(module)s", "function": "%(funcName)s", "line": %(lineno)d}',
                "datefmt": "%Y-%m-%dT%H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "standard",
                "stream": sys.stdout
            }
        },
        "loggers": {
            # Application loggers
            "backend": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False
            },
            "backend.app_kernel": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False
            },
            "backend.middleware": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False
            },
            "backend.kernel_agents": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False
            },
            # Azure SDK loggers - reduce verbosity
            "azure": {
                "level": logging.WARNING,
                "handlers": ["console"],
                "propagate": False
            },
            "azure.monitor": {
                "level": logging.WARNING,
                "handlers": ["console"],
                "propagate": False
            },
            "azure.cosmos": {
                "level": logging.WARNING,
                "handlers": ["console"],
                "propagate": False
            },
            "azure.ai": {
                "level": logging.WARNING,
                "handlers": ["console"],
                "propagate": False
            },
            # OpenTelemetry loggers - reduce verbosity
            "opentelemetry": {
                "level": logging.WARNING,
                "handlers": ["console"],
                "propagate": False
            },
            # HTTP client loggers - reduce verbosity
            "httpx": {
                "level": logging.WARNING,
                "handlers": ["console"],
                "propagate": False
            },
            "httpcore": {
                "level": logging.WARNING,
                "handlers": ["console"],
                "propagate": False
            },
            # FastAPI/Uvicorn loggers
            "uvicorn": {
                "level": logging.INFO,
                "handlers": ["console"],
                "propagate": False
            },
            "uvicorn.error": {
                "level": logging.INFO,
                "handlers": ["console"],
                "propagate": False
            },
            "uvicorn.access": {
                "level": logging.INFO,
                "handlers": ["console"],
                "propagate": False
            }
        },
        "root": {
            "level": log_level,
            "handlers": ["console"]
        }
    }
    
    # Add file handler if requested
    if enable_file_logging:
        if not log_file_path:
            log_file_path = os.getenv("LOG_FILE", "darbot_engine.log")
        
        config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": log_level,
            "formatter": "detailed",
            "filename": log_file_path,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        }
        
        # Add file handler to all loggers
        for logger_config in config["loggers"].values():
            if "handlers" in logger_config:
                logger_config["handlers"].append("file")
        
        config["root"]["handlers"].append("file")
    
    # Apply the configuration
    logging.config.dictConfig(config)
    
    # Log the setup
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level: {logging.getLevelName(log_level)}")
    logger.info(f"File logging: {'enabled' if enable_file_logging else 'disabled'}")
    if enable_file_logging:
        logger.info(f"Log file: {log_file_path}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


# Environment-based configuration
def configure_for_environment() -> None:
    """Configure logging based on environment variables"""
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment == "production":
        # Production: JSON format, file logging, WARNING level
        setup_logging(
            log_level=logging.WARNING,
            enable_file_logging=True,
            log_file_path="/var/log/darbot_engine.log"
        )
    elif environment == "staging":
        # Staging: Standard format, file logging, INFO level
        setup_logging(
            log_level=logging.INFO,
            enable_file_logging=True,
            log_file_path="/tmp/darbot_engine.log"
        )
    else:
        # Development: Console only, DEBUG level
        setup_logging(
            log_level=logging.DEBUG,
            enable_file_logging=False
        )