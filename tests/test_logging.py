"""
Test Suite for Logging System
"""

import pytest
import logging
from pathlib import Path
import tempfile
from tools.core.logging_config import setup_logging, SafeFileOperations


class TestLoggingSetup:
    """Test logging configuration"""

    def test_logging_initialization(self):
        """Logging should initialize without errors"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir)
            setup_logging(log_dir, 'DEBUG')

            # Check that logger was configured
            logger = logging.getLogger()
            assert logger.level == logging.DEBUG
            assert len(logger.handlers) > 0

    def test_log_directory_creation(self):
        """Log directory should be created if it doesn't exist"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            setup_logging(log_dir, 'INFO')
            assert log_dir.exists()

    def test_file_handler_creation(self):
        """File handlers should be created"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir)
            setup_logging(log_dir, 'INFO')

            # Log a message
            logger = logging.getLogger('test')
            logger.info("Test message")

            # Check that log file was created
            log_files = list(log_dir.glob("songs-gen-*.log"))
            assert len(log_files) > 0


class TestSafeFileOperations:
    """Test safe file operations"""

    def test_safe_read_existing_file(self):
        """Should read existing file"""
        ops = SafeFileOperations()
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            f.flush()
            temp_path = Path(f.name)

        try:
            content = ops.safe_read_file(temp_path)
            assert content == "test content"
        finally:
            temp_path.unlink()

    def test_safe_read_missing_file(self):
        """Should handle missing file gracefully"""
        ops = SafeFileOperations()
        missing_path = Path("/nonexistent/file.txt")
        content = ops.safe_read_file(missing_path)
        assert content == ""

    def test_safe_write_file(self):
        """Should write file successfully"""
        ops = SafeFileOperations()
        with tempfile.TemporaryDirectory() as tmpdir:
            test_path = Path(tmpdir) / "test.txt"
            success = ops.safe_write_file(test_path, "test content")

            assert success
            assert test_path.exists()
            assert test_path.read_text() == "test content"

    def test_safe_write_creates_directories(self):
        """Should create parent directories"""
        ops = SafeFileOperations()
        with tempfile.TemporaryDirectory() as tmpdir:
            test_path = Path(tmpdir) / "subdir" / "test.txt"
            success = ops.safe_write_file(test_path, "test content")

            assert success
            assert test_path.exists()
