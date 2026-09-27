#!/bin/zsh
# Shared single-writer lock for every scheduled Coral wiki job.

acquire_coral_lock() {
    LOCK_DIR="$1/logs/.wiki-writer.lock"
    mkdir -p "$1/logs"
    if mkdir "$LOCK_DIR" 2>/dev/null; then
        echo "$PPID:$$" > "$LOCK_DIR/owner"
        trap 'rm -rf "$LOCK_DIR"' EXIT INT TERM
        return 0
    fi
    echo "Another Coral wiki writer owns $LOCK_DIR; skipping this run" >&2
    return 75
}
