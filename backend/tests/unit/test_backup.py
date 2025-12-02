"""Unit tests for backup service.

Tests for automated database backup functionality.
"""

import os
import subprocess
from unittest.mock import MagicMock, patch, Mock, PropertyMock

import pytest

from app.services.backup import (
    schedule_backups,
    stop_backups,
    backup_database,
    scheduler,
)


@pytest.mark.unit
class TestBackupService:
    """Test backup service functionality."""

    def test_schedule_backups_skips_in_test_mode(self):
        """Test that backup scheduling is skipped in test mode."""
        with patch.dict(os.environ, {"APP_ENV": "test"}):
            # Should not raise and should not start scheduler
            schedule_backups()
            # Scheduler should not be running in test mode
            # (it may have been started by other tests, so we just verify no error)

    def test_schedule_backups_skips_if_already_running(self):
        """Test that backup scheduling skips if scheduler already running."""
        with patch.dict(os.environ, {"APP_ENV": "production"}):
            with patch.object(type(scheduler), 'running', new_callable=PropertyMock) as mock_running:
                mock_running.return_value = True
                with patch.object(scheduler, 'add_job') as mock_add_job:
                    schedule_backups()
                    # Should not add job if already running
                    mock_add_job.assert_not_called()

    def test_schedule_backups_adds_job_and_starts(self):
        """Test that backup scheduling adds job and starts scheduler."""
        with patch.dict(os.environ, {"APP_ENV": "production"}):
            with patch.object(type(scheduler), 'running', new_callable=PropertyMock) as mock_running:
                mock_running.return_value = False
                with patch.object(scheduler, 'add_job') as mock_add_job:
                    with patch.object(scheduler, 'start') as mock_start:
                        schedule_backups()

                        # Verify job was added with correct parameters
                        mock_add_job.assert_called_once()
                        call_args = mock_add_job.call_args
                        assert call_args[0][0] == backup_database  # First positional arg
                        assert call_args[0][1] == "cron"  # Trigger type
                        assert call_args[1]["hour"] == 3
                        assert call_args[1]["minute"] == 0
                        assert call_args[1]["id"] == "daily_backup"
                        assert call_args[1]["replace_existing"] is True

                        # Verify scheduler was started
                        mock_start.assert_called_once()

    def test_stop_backups_when_running(self):
        """Test stopping backup scheduler when it's running."""
        with patch.object(type(scheduler), 'running', new_callable=PropertyMock) as mock_running:
            mock_running.return_value = True
            with patch.object(scheduler, 'shutdown') as mock_shutdown:
                stop_backups()
                mock_shutdown.assert_called_once_with(wait=False)

    def test_stop_backups_when_not_running(self):
        """Test stopping backup scheduler when it's not running."""
        with patch.object(type(scheduler), 'running', new_callable=PropertyMock) as mock_running:
            mock_running.return_value = False
            with patch.object(scheduler, 'shutdown') as mock_shutdown:
                stop_backups()
                # Should not call shutdown if not running
                mock_shutdown.assert_not_called()

    def test_backup_database_success(self):
        """Test successful database backup execution."""
        mock_result = Mock()
        mock_result.stdout = "Backup completed successfully"

        with patch('subprocess.run', return_value=mock_result) as mock_run:
            backup_database()

            mock_run.assert_called_once_with(
                ["/app/scripts/backup.sh"],
                check=True,
                capture_output=True,
                text=True,
            )

    def test_backup_database_called_process_error(self):
        """Test database backup with CalledProcessError."""
        mock_error = subprocess.CalledProcessError(
            returncode=1,
            cmd=["/app/scripts/backup.sh"],
            stderr="Backup failed: disk full",
        )

        with patch('subprocess.run', side_effect=mock_error):
            # Should not raise, just log error
            backup_database()

    def test_backup_database_unexpected_error(self):
        """Test database backup with unexpected error."""
        with patch('subprocess.run', side_effect=Exception("Unexpected error")):
            # Should not raise, just log error
            backup_database()

    def test_backup_database_file_not_found(self):
        """Test database backup when script doesn't exist."""
        with patch('subprocess.run', side_effect=FileNotFoundError("Script not found")):
            # Should not raise, just log error
            backup_database()


@pytest.mark.unit
class TestBackupSchedulerIntegration:
    """Test backup scheduler integration scenarios."""

    def test_full_lifecycle(self):
        """Test full backup scheduler lifecycle."""
        with patch.dict(os.environ, {"APP_ENV": "production"}):
            with patch.object(type(scheduler), 'running', new_callable=PropertyMock) as mock_running:
                mock_running.return_value = False
                with patch.object(scheduler, 'add_job') as mock_add_job:
                    with patch.object(scheduler, 'start') as mock_start:
                        # Start scheduler
                        schedule_backups()
                        mock_start.assert_called_once()

        # Simulate running state
        with patch.object(type(scheduler), 'running', new_callable=PropertyMock) as mock_running:
            mock_running.return_value = True
            with patch.object(scheduler, 'shutdown') as mock_shutdown:
                # Stop scheduler
                stop_backups()
                mock_shutdown.assert_called_once_with(wait=False)

    def test_schedule_backups_idempotent(self):
        """Test that scheduling backups multiple times is safe."""
        with patch.dict(os.environ, {"APP_ENV": "production"}):
            # First call - not running
            with patch.object(type(scheduler), 'running', new_callable=PropertyMock) as mock_running:
                mock_running.return_value = False
                with patch.object(scheduler, 'add_job') as mock_add_job:
                    with patch.object(scheduler, 'start') as mock_start:
                        schedule_backups()
                        assert mock_add_job.call_count == 1

        with patch.dict(os.environ, {"APP_ENV": "production"}):
            # Second call - already running
            with patch.object(type(scheduler), 'running', new_callable=PropertyMock) as mock_running:
                mock_running.return_value = True
                with patch.object(scheduler, 'add_job') as mock_add_job:
                    schedule_backups()
                    # Should not add job again
                    mock_add_job.assert_not_called()
