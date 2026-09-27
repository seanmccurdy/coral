#!/bin/zsh
# Scheduled coral wiki update (invoked by launchd; safe to run manually).
# Caps videos per run so the backlog drains gradually — raise or drop the
# cap by editing CORAL_MAX_VIDEOS here or in the environment.
set -uo pipefail

REPO="/Users/hyprbm/Developer/coral"
LOG_DIR="$REPO/logs"
MAX_VIDEOS="${CORAL_MAX_VIDEOS:-15}"

# launchd starts with a minimal PATH; uv and claude live in user dirs.
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
source "$REPO/scripts/coral-lock.sh"
acquire_coral_lock "$REPO" || exit $?

mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/update-$(date +%Y-%m-%d).log"

{
    echo "=== coral update started $(date) (max $MAX_VIDEOS videos) ==="
    cd "$REPO" || exit 1
    uv run python update_wiki.py --limit-videos "$MAX_VIDEOS"
    rc=$?
    if [[ $rc -eq 0 ]]; then
        uv run python update_wiki.py --validate-wiki
        rc=$?
    fi
    echo "=== finished $(date) exit=$rc ==="
    exit $rc
} >> "$LOG" 2>&1
