"""
Centralized logging configuration for Songs Generation System
"""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
import sys


def setup_logging(log_dir: Path = None, level: str = 'INFO'):
    """
    Setup comprehensive logging system

    Args:
        log_dir: Directory for log files (default: project root/logs)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    if log_dir is None:
        # Find project root
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent
        log_dir = project_root / "logs"

    log_dir.mkdir(exist_ok=True)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Clear existing handlers
    root_logger.handlers.clear()

    # Console handler (user-friendly)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler (detailed)
    log_file = log_dir / f"songs-gen-{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # Error file handler (errors only)
    error_file = log_dir / f"errors-{datetime.now().strftime('%Y%m%d')}.log"
    error_handler = logging.FileHandler(error_file)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    root_logger.addHandler(error_handler)

    root_logger.info(f"Logging configured - Level: {level}")
    root_logger.debug(f"Log files: {log_dir}")


class SafeFileOperations:
    """Wrapper for file operations with comprehensive error handling"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def safe_read_file(self, filepath: Path) -> str:
        """
        Safely read file with comprehensive error handling

        Returns:
            File content or empty string if error
        """
        try:
            self.logger.debug(f"Reading file: {filepath}")

            if not filepath.exists():
                self.logger.error(f"File not found: {filepath}")
                return ""

            if not filepath.is_file():
                self.logger.error(f"Not a file: {filepath}")
                return ""

            content = filepath.read_text(encoding='utf-8')
            self.logger.debug(f"Successfully read {len(content)} bytes")
            return content

        except PermissionError:
            self.logger.error(f"Permission denied: {filepath}")
            return ""
        except UnicodeDecodeError as e:
            self.logger.error(f"Encoding error in {filepath}: {e}")
            return ""
        except Exception as e:
            self.logger.exception(f"Unexpected error reading {filepath}")
            return ""

    def safe_write_file(self, filepath: Path, content: str) -> bool:
        """
        Safely write file with error handling

        Returns:
            True if successful
        """
        try:
            self.logger.debug(f"Writing to file: {filepath}")

            # Create parent directories
            filepath.parent.mkdir(parents=True, exist_ok=True)

            # Write content
            filepath.write_text(content, encoding='utf-8')

            # Verify write
            if not filepath.exists():
                self.logger.error(f"Write verification failed: {filepath}")
                return False

            self.logger.info(f"Successfully wrote {len(content)} bytes to {filepath}")
            return True

        except PermissionError:
            self.logger.error(f"Permission denied: {filepath}")
            return False
        except OSError as e:
            self.logger.error(f"OS error writing to {filepath}: {e}")
            return False
        except Exception as e:
            self.logger.exception(f"Unexpected error writing to {filepath}")
            return False
