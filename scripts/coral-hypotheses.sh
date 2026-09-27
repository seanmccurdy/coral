#!/bin/zsh
# Weekly bounded hypothesis workshop (invoked by launchd; safe to run manually).
set -uo pipefail

REPO="/Users/hyprbm/Developer/coral"
LOG_DIR="$REPO/logs"
MAX_NEW="${CORAL_MAX_NEW_HYPOTHESES:-1}"

export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
source "$REPO/scripts/coral-lock.sh"
acquire_coral_lock "$REPO" || exit $?

mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/hypotheses-$(date +%Y-%m-%d).log"

{
    echo "=== coral hypothesis workshop started $(date) (max $MAX_NEW new) ==="
    cd "$REPO" || exit 1
    uv run python update_wiki.py --develop-hypotheses --max-new-hypotheses "$MAX_NEW" --engine codex
    rc=$?
    if [[ $rc -eq 0 ]]; then
        uv run python update_wiki.py --validate-wiki
        rc=$?
    fi
    echo "=== finished $(date) exit=$rc ==="
    exit $rc
} >> "$LOG" 2>&1
