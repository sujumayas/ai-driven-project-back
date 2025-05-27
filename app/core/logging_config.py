import logging
import sys
from typing import Dict, Any

def configure_logging() -> Dict[str, Any]:
    """Configure logging for the application."""
    
    # Set SQLAlchemy logging to WARNING to reduce verbosity
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.dialects").setLevel(logging.WARNING)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Return logging config for uvicorn
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "root": {
            "level": "INFO",
            "handlers": ["default"],
        },
        "loggers": {
            "sqlalchemy.engine": {
                "level": "WARNING",
                "handlers": ["default"],
                "propagate": False,
            },
            "sqlalchemy.pool": {
                "level": "WARNING", 
                "handlers": ["default"],
                "propagate": False,
            },
            "sqlalchemy.dialects": {
                "level": "WARNING",
                "handlers": ["default"], 
                "propagate": False,
            },
        }
    }
