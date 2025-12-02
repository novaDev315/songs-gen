#!/bin/bash
# File watcher service management script
# Similar to suno_service.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PID_FILE="$PROJECT_DIR/data/file_watcher.pid"
LOG_FILE="$PROJECT_DIR/data/file_watcher.log"

cd "$PROJECT_DIR" || exit 1

start() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "File watcher is already running (PID: $PID)"
            return 1
        fi
    fi

    echo "Starting file watcher..."
    mkdir -p "$PROJECT_DIR/data"

    # Run in background with unbuffered output
    nohup python -u tools/file_watcher.py >> "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"

    sleep 2
    if ps -p $(cat "$PID_FILE") > /dev/null 2>&1; then
        echo "File watcher started (PID: $(cat "$PID_FILE"))"
        echo "Log file: $LOG_FILE"
    else
        echo "Failed to start file watcher"
        rm -f "$PID_FILE"
        return 1
    fi
}

stop() {
    if [ ! -f "$PID_FILE" ]; then
        echo "File watcher is not running (no PID file)"
        return 0
    fi

    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "Stopping file watcher (PID: $PID)..."
        kill "$PID"
        sleep 2
        if ps -p "$PID" > /dev/null 2>&1; then
            kill -9 "$PID"
        fi
        echo "File watcher stopped"
    else
        echo "File watcher is not running"
    fi
    rm -f "$PID_FILE"
}

status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "File watcher is running (PID: $PID)"
            return 0
        else
            echo "File watcher is not running (stale PID file)"
            return 1
        fi
    else
        echo "File watcher is not running"
        return 1
    fi
}

logs() {
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE"
    else
        echo "No log file found at $LOG_FILE"
    fi
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        sleep 1
        start
        ;;
    status)
        status
        ;;
    logs)
        logs
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        exit 1
        ;;
esac
