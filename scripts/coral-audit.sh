#!/bin/zsh
# Monthly stale-evidence, correction, and synthesis reconciliation.
set -uo pipefail

REPO="/Users/hyprbm/Developer/coral"
LOG_DIR="$REPO/logs"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
source "$REPO/scripts/coral-lock.sh"
acquire_coral_lock "$REPO" || exit $?

mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/audit-$(date +%Y-%m-%d).log"

{
    echo "=== coral monthly audit started $(date) ==="
    cd "$REPO" || exit 1
    uv run python update_wiki.py --check-sources
    source_rc=$?
    uv run python update_wiki.py --audit-wiki --audit-pages 8 --engine codex
    rc=$?
    if [[ $source_rc -ne 0 && $rc -eq 0 ]]; then
        rc=$source_rc
    fi
    if [[ $rc -eq 0 ]]; then
        uv run python update_wiki.py --validate-wiki
        rc=$?
    fi
    echo "=== finished $(date) exit=$rc ==="
    exit $rc
} >> "$LOG" 2>&1
