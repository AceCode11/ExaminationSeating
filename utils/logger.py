import logging
from logging.handlers import RotatingFileHandler
import os
from core.constants import LOG_DIR, LOG_FILE, LOG_MAX_BYTES, LOG_BACKUP_COUNT

def setup_logging():
    """Configure enterprise-level rotating file logging."""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
        
    log_path = os.path.join(LOG_DIR, LOG_FILE)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    file_handler = RotatingFileHandler(
        log_path, 
        maxBytes=LOG_MAX_BYTES, 
        backupCount=LOG_BACKUP_COUNT
    )
    file_handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Avoid adding duplicate handlers if setup_logging is called multiple times
    if not root_logger.handlers:
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

def get_logger(name: str) -> logging.Logger:
    """Get a named logger instance."""
    return logging.getLogger(name)
