#!/bin/bash
set -e

# Configuration
BACKUP_DIR="/app/data/backups"
DB_FILE="/app/data/songs.db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/songs_$TIMESTAMP.db"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "Starting database backup..."

# Create backup using SQLite's built-in backup command
sqlite3 "$DB_FILE" ".backup '$BACKUP_FILE'"

# Compress the backup
echo "Compressing backup..."
gzip "$BACKUP_FILE"

# Keep only last 30 days of backups
echo "Cleaning up old backups (keeping last 30 days)..."
find "$BACKUP_DIR" -name "songs_*.db.gz" -mtime +30 -delete

# Verify backup integrity
echo "Verifying backup integrity..."
gunzip -c "$BACKUP_FILE.gz" | sqlite3 :memory: "PRAGMA integrity_check;" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "Backup completed successfully: $BACKUP_FILE.gz"
else
    echo "ERROR: Backup verification failed!"
    exit 1
fi

# Show backup info
BACKUP_SIZE=$(du -h "$BACKUP_FILE.gz" | cut -f1)
echo "Backup size: $BACKUP_SIZE"
echo "Backup location: $BACKUP_FILE.gz"
