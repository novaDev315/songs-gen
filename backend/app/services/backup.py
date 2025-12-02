"""Backup service for database and file backups."""

import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Global scheduler instance
_scheduler: Optional[AsyncIOScheduler] = None


def get_backup_path() -> Path:
    """Get the backup directory path."""
    backup_path = Path(settings.BACKUP_PATH)
    backup_path.mkdir(parents=True, exist_ok=True)
    return backup_path


def create_database_backup() -> Optional[Path]:
    """Create a backup of the SQLite database."""
    try:
        db_url = settings.DATABASE_URL

        # Only backup SQLite databases
        if not db_url.startswith("sqlite"):
            logger.info("Database backup only supported for SQLite")
            return None

        # Extract database file path
        db_path = db_url.replace("sqlite+aiosqlite:///", "").replace("sqlite:///", "")
        db_file = Path(db_path)

        if not db_file.exists():
            logger.warning(f"Database file not found: {db_file}")
            return None

        # Create backup with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = get_backup_path()
        backup_file = backup_dir / f"songs_backup_{timestamp}.db"

        # Copy database file
        shutil.copy2(db_file, backup_file)
        logger.info(f"Database backup created: {backup_file}")

        # Cleanup old backups (keep last 7 days)
        cleanup_old_backups(backup_dir, max_age_days=7)

        return backup_file

    except Exception as e:
        logger.error(f"Failed to create database backup: {e}")
        return None


def create_generated_backup() -> Optional[Path]:
    """Create a backup of generated files (audio, covers, etc.)."""
    try:
        generated_path = Path(settings.GENERATED_PATH)

        if not generated_path.exists():
            logger.warning(f"Generated path not found: {generated_path}")
            return None

        # Create backup with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = get_backup_path()
        backup_archive = backup_dir / f"generated_backup_{timestamp}"

        # Create archive
        shutil.make_archive(
            str(backup_archive),
            "zip",
            generated_path
        )

        backup_file = Path(f"{backup_archive}.zip")
        logger.info(f"Generated files backup created: {backup_file}")

        return backup_file

    except Exception as e:
        logger.error(f"Failed to create generated files backup: {e}")
        return None


def cleanup_old_backups(backup_dir: Path, max_age_days: int = 7) -> int:
    """Remove backups older than max_age_days."""
    removed_count = 0
    cutoff = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)

    try:
        for backup_file in backup_dir.glob("*_backup_*"):
            if backup_file.stat().st_mtime < cutoff:
                backup_file.unlink()
                logger.info(f"Removed old backup: {backup_file.name}")
                removed_count += 1

    except Exception as e:
        logger.error(f"Error cleaning up old backups: {e}")

    return removed_count


async def run_scheduled_backup() -> None:
    """Run scheduled backup job."""
    logger.info("Running scheduled backup...")

    # Create database backup
    db_backup = create_database_backup()
    if db_backup:
        logger.info(f"Database backup completed: {db_backup}")

    # Optionally backup generated files (can be expensive)
    if settings.BACKUP_GENERATED_FILES:
        gen_backup = create_generated_backup()
        if gen_backup:
            logger.info(f"Generated files backup completed: {gen_backup}")

    logger.info("Scheduled backup completed")


def schedule_backups() -> None:
    """Schedule automatic backups."""
    global _scheduler

    if not settings.ENABLE_BACKUPS:
        logger.info("Automatic backups disabled")
        return

    _scheduler = AsyncIOScheduler()

    # Schedule daily backup at 3 AM
    _scheduler.add_job(
        run_scheduled_backup,
        CronTrigger(hour=3, minute=0),
        id="daily_backup",
        name="Daily database backup",
        replace_existing=True,
    )

    _scheduler.start()
    logger.info("Backup scheduler started - daily backups at 3:00 AM")


def stop_scheduler() -> None:
    """Stop the backup scheduler."""
    global _scheduler
    if _scheduler:
        _scheduler.shutdown()
        _scheduler = None
        logger.info("Backup scheduler stopped")


async def manual_backup(include_generated: bool = False) -> dict:
    """Perform a manual backup."""
    results = {
        "database": None,
        "generated": None,
        "success": True,
    }

    # Database backup
    db_backup = create_database_backup()
    if db_backup:
        results["database"] = str(db_backup)
    else:
        results["success"] = False

    # Generated files backup if requested
    if include_generated:
        gen_backup = create_generated_backup()
        if gen_backup:
            results["generated"] = str(gen_backup)

    return results


def list_backups() -> list[dict]:
    """List all available backups."""
    backup_dir = get_backup_path()
    backups = []

    for backup_file in sorted(backup_dir.glob("*_backup_*"), key=lambda x: x.stat().st_mtime, reverse=True):
        backups.append({
            "name": backup_file.name,
            "path": str(backup_file),
            "size": backup_file.stat().st_size,
            "created": datetime.fromtimestamp(backup_file.stat().st_mtime).isoformat(),
            "type": "database" if backup_file.suffix == ".db" else "generated",
        })

    return backups
