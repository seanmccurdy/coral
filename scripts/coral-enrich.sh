#!/bin/zsh
# Weekly evidence-enrichment pass (invoked by launchd; safe to run manually).
set -uo pipefail

REPO="/Users/hyprbm/Developer/coral"
LOG_DIR="$REPO/logs"
PAGES="${CORAL_ENRICH_PAGES:-2}"

export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
source "$REPO/scripts/coral-lock.sh"
acquire_coral_lock "$REPO" || exit $?

mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/enrich-$(date +%Y-%m-%d).log"

{
    echo "=== coral enrichment started $(date) (max $PAGES items) ==="
    cd "$REPO" || exit 1
    uv run python update_wiki.py --enrich-wiki --pages "$PAGES" --engine codex
    rc=$?
    if [[ $rc -eq 0 ]]; then
        uv run python update_wiki.py --validate-wiki
        rc=$?
    fi
    echo "=== finished $(date) exit=$rc ==="
    exit $rc
} >> "$LOG" 2>&1
