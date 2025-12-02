#!/bin/bash
# Suno Worker Service
# Runs the Suno worker continuously in the background
#
# Usage:
#   ./tools/suno_service.sh start   - Start the worker
#   ./tools/suno_service.sh stop    - Stop the worker
#   ./tools/suno_service.sh status  - Check if running
#   ./tools/suno_service.sh logs    - View logs

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PID_FILE="$PROJECT_DIR/data/suno_worker.pid"
LOG_FILE="$PROJECT_DIR/data/suno_worker.log"

cd "$PROJECT_DIR"

start_worker() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "Worker already running (PID: $PID)"
            return 1
        fi
    fi

    echo "Starting Suno worker..."
    mkdir -p "$(dirname "$LOG_FILE")"

    # Run worker in background with nohup
    nohup python tools/suno_worker.py --interval 30 >> "$LOG_FILE" 2>&1 &
    PID=$!
    echo $PID > "$PID_FILE"

    sleep 2
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "Worker started (PID: $PID)"
        echo "Logs: $LOG_FILE"
    else
        echo "Failed to start worker. Check logs: $LOG_FILE"
        rm -f "$PID_FILE"
        return 1
    fi
}

stop_worker() {
    if [ ! -f "$PID_FILE" ]; then
        echo "Worker not running (no PID file)"
        return 0
    fi

    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "Stopping worker (PID: $PID)..."
        kill "$PID"
        sleep 2
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "Force killing..."
            kill -9 "$PID"
        fi
        echo "Worker stopped"
    else
        echo "Worker not running"
    fi
    rm -f "$PID_FILE"
}

status_worker() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "Worker running (PID: $PID)"
            echo "Uptime: $(ps -o etime= -p "$PID" | xargs)"
            return 0
        fi
    fi
    echo "Worker not running"
    return 1
}

show_logs() {
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE"
    else
        echo "No logs found at $LOG_FILE"
    fi
}

case "$1" in
    start)
        start_worker
        ;;
    stop)
        stop_worker
        ;;
    restart)
        stop_worker
        sleep 1
        start_worker
        ;;
    status)
        status_worker
        ;;
    logs)
        show_logs
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        exit 1
        ;;
esac
