"""
Simple universal logger for the data migration project
"""

import logging
import sys
from pathlib import Path

# ANSI color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# Emoji icons for different log levels
class Icons:
    DEBUG = "🔍"
    INFO = "ℹ️"
    WARNING = "⚠️"
    ERROR = "❌"
    CRITICAL = "🚨"
    SUCCESS = "✅"
    DATABASE = "🗄️"
    API = "🌐"
    STARTUP = "🚀"
    SHUTDOWN = "🛑"

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors and emojis for different log levels"""
    
    COLORS = {
        'DEBUG': Colors.CYAN,
        'INFO': Colors.GREEN,
        'WARNING': Colors.YELLOW,
        'ERROR': Colors.RED,
        'CRITICAL': Colors.RED + Colors.BOLD,
    }
    
    ICONS = {
        'DEBUG': Icons.DEBUG,
        'INFO': Icons.INFO,
        'WARNING': Icons.WARNING,
        'ERROR': Icons.ERROR,
        'CRITICAL': Icons.CRITICAL,
    }
    
    def format(self, record):
        # Add icon and color to the levelname
        if record.levelname in self.COLORS:
            icon = self.ICONS.get(record.levelname, "")
            record.levelname = f"{self.COLORS[record.levelname]}{icon} {record.levelname}{Colors.END}"
        
        # Add color to the message for certain levels
        if record.levelname == 'ERROR' or 'ERROR' in record.levelname:
            record.msg = f"{Colors.RED}{record.msg}{Colors.END}"
        elif record.levelname == 'WARNING' or 'WARNING' in record.levelname:
            record.msg = f"{Colors.YELLOW}{record.msg}{Colors.END}"
        elif record.levelname == 'INFO' or 'INFO' in record.levelname:
            record.msg = f"{Colors.GREEN}{record.msg}{Colors.END}"
        
        return super().format(record)

def setup_logger(name: str = "data_migration", level: str = "INFO") -> logging.Logger:
    """
    Setup a simple logger with colored console and file output
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Create formatters
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    # File handler (no colors in file)
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    file_handler = logging.FileHandler(log_dir / "data_migration.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# Create default logger instance
logger = setup_logger()

def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance
    
    Args:
        name: Optional logger name (uses default if None)
    
    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f"data_migration.{name}")
    return logger 