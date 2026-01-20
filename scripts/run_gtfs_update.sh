#!/usr/bin/env bash
set -e

# PROJECT_DIR="/opt/telegram-bot-sofia-transport"
PROJECT_DIR="/home/lika/Projects/Telegram-bot-sofia-transport"
VENV="$PROJECT_DIR/.venv/bin/python"
LOG_FILE="$PROJECT_DIR/logs/gtfs_update.log"

mkdir -p "$PROJECT_DIR/logs"

cd "$PROJECT_DIR" || exit 1

echo "=== $(date) GTFS update started ===" >> "$LOG_FILE"

$VENV -m transport.cli.update_gtfs >> "$LOG_FILE" 2>&1

STATUS=$?

if [ $STATUS -ne 0 ]; then
  echo "GTFS update failed with exit code $STATUS" >> "$LOG_FILE"
  # ← здесь Telegram / webhook
fi

echo "=== $(date) GTFS update finished ===" >> "$LOG_FILE"
