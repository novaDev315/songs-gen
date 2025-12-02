#!/bin/bash
# Unified service management for all local tools
# Usage: ./tools/services.sh {start|stop|restart|status|logs} [service]
# Services: all, watcher, suno

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$PROJECT_DIR/data"

# Service definitions
declare -A SERVICES=(
    ["watcher"]="file_watcher.py"
    ["suno"]="suno_worker.py"
)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

cd "$PROJECT_DIR" || exit 1
mkdir -p "$DATA_DIR"

get_pid_file() {
    echo "$DATA_DIR/${1}.pid"
}

get_log_file() {
    echo "$DATA_DIR/${1}.log"
}

is_running() {
    local service=$1
    local pid_file=$(get_pid_file "$service")

    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

start_service() {
    local service=$1
    local script=${SERVICES[$service]}
    local pid_file=$(get_pid_file "$service")
    local log_file=$(get_log_file "$service")

    if is_running "$service"; then
        echo -e "${YELLOW}$service is already running (PID: $(cat "$pid_file"))${NC}"
        return 1
    fi

    echo -n "Starting $service... "

    # Build command based on service
    local cmd="python -u tools/$script"

    # Add service-specific args
    case $service in
        suno)
            cmd="$cmd --interval 30 --batch-size 5"
            ;;
        watcher)
            cmd="$cmd --scan-existing"
            ;;
    esac

    # Set display for suno worker (browser automation)
    export DISPLAY="${DISPLAY:-:0}"
    export XAUTHORITY="${XAUTHORITY:-$HOME/.Xauthority}"

    # Run in background
    nohup $cmd >> "$log_file" 2>&1 &
    echo $! > "$pid_file"

    sleep 2
    if is_running "$service"; then
        echo -e "${GREEN}started (PID: $(cat "$pid_file"))${NC}"
        return 0
    else
        echo -e "${RED}failed${NC}"
        rm -f "$pid_file"
        echo "Check logs: $log_file"
        return 1
    fi
}

stop_service() {
    local service=$1
    local pid_file=$(get_pid_file "$service")

    if [ ! -f "$pid_file" ]; then
        echo -e "${YELLOW}$service is not running (no PID file)${NC}"
        return 0
    fi

    local pid=$(cat "$pid_file")
    echo -n "Stopping $service (PID: $pid)... "

    if ps -p "$pid" > /dev/null 2>&1; then
        kill "$pid" 2>/dev/null
        sleep 2

        if ps -p "$pid" > /dev/null 2>&1; then
            kill -9 "$pid" 2>/dev/null
            sleep 1
        fi
    fi

    rm -f "$pid_file"
    echo -e "${GREEN}stopped${NC}"
}

status_service() {
    local service=$1
    local pid_file=$(get_pid_file "$service")

    echo -n "$service: "
    if is_running "$service"; then
        echo -e "${GREEN}running (PID: $(cat "$pid_file"))${NC}"
    else
        echo -e "${RED}stopped${NC}"
    fi
}

logs_service() {
    local service=$1
    local log_file=$(get_log_file "$service")

    if [ -f "$log_file" ]; then
        tail -f "$log_file"
    else
        echo "No log file found: $log_file"
    fi
}

# Determine which services to operate on
get_services() {
    local target=$1

    if [ "$target" = "all" ] || [ -z "$target" ]; then
        echo "${!SERVICES[@]}"
    elif [ -n "${SERVICES[$target]}" ]; then
        echo "$target"
    else
        echo ""
    fi
}

# Main command handler
ACTION=$1
TARGET=${2:-all}

case "$ACTION" in
    start)
        echo "=============================================="
        echo "STARTING SERVICES"
        echo "=============================================="
        for svc in $(get_services "$TARGET"); do
            start_service "$svc"
        done
        echo ""
        echo "Logs: $DATA_DIR/*.log"
        echo "Stop: ./tools/services.sh stop"
        ;;

    stop)
        echo "=============================================="
        echo "STOPPING SERVICES"
        echo "=============================================="
        for svc in $(get_services "$TARGET"); do
            stop_service "$svc"
        done
        ;;

    restart)
        echo "=============================================="
        echo "RESTARTING SERVICES"
        echo "=============================================="
        for svc in $(get_services "$TARGET"); do
            stop_service "$svc"
        done
        sleep 1
        for svc in $(get_services "$TARGET"); do
            start_service "$svc"
        done
        ;;

    status)
        echo "=============================================="
        echo "SERVICE STATUS"
        echo "=============================================="
        for svc in $(get_services "$TARGET"); do
            status_service "$svc"
        done
        ;;

    logs)
        if [ "$TARGET" = "all" ]; then
            # Show all logs with multitail or combined
            echo "Showing combined logs (Ctrl+C to exit)..."
            tail -f "$DATA_DIR"/*.log 2>/dev/null
        else
            logs_service "$TARGET"
        fi
        ;;

    *)
        echo "=============================================="
        echo "SONGS-GEN LOCAL SERVICES"
        echo "=============================================="
        echo ""
        echo "Usage: $0 {start|stop|restart|status|logs} [service]"
        echo ""
        echo "Services:"
        echo "  all     - All services (default)"
        echo "  watcher - File watcher (monitors generated/songs)"
        echo "  suno    - Suno worker (uploads to Suno AI)"
        echo ""
        echo "Examples:"
        echo "  $0 start           # Start all services"
        echo "  $0 start suno      # Start only Suno worker"
        echo "  $0 stop            # Stop all services"
        echo "  $0 status          # Check all service status"
        echo "  $0 logs suno       # Follow Suno worker logs"
        echo "  $0 logs            # Follow all logs"
        echo ""
        exit 1
        ;;
esac
