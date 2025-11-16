"""Automated database backup service."""

import logging
import subprocess

from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def schedule_backups() -> None:
    """Schedule daily backups at 3 AM."""
    scheduler.add_job(
        backup_database,
        "cron",
        hour=3,
        minute=0,
        id="daily_backup",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Backup scheduler started (daily at 3 AM)")


def backup_database() -> None:
    """Execute database backup script."""
    try:
        result = subprocess.run(
            ["/app/scripts/backup.sh"],
            check=True,
            capture_output=True,
            text=True,
        )
        logger.info(f"Database backup completed successfully: {result.stdout}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Database backup failed: {e.stderr}")
    except Exception as e:
        logger.error(f"Unexpected error during backup: {e}")
