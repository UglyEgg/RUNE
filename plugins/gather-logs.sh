#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
. "${SCRIPT_DIR}/lib/rune_bpcs.sh"

rune_init
WORK_DIR=$(mktemp -d /tmp/rune-logs-XXXXXX)
ARTIFACT=$(mktemp /tmp/rune-logs-XXXXXX.tar.gz)
ENTRIES=0

journal_since=$(rune_param "journal_since" "")
extra_paths_json=$(rune_param_json "extra_paths" "[]")

include_file() {
  local path="$1"
  if [[ -f "$path" ]]; then
    cp "$path" "$WORK_DIR"/$(basename "$path") 2>/dev/null || true
    ENTRIES=$((ENTRIES + 1))
  fi
}

if command -v journalctl >/dev/null 2>&1; then
  if [[ -n "$journal_since" ]]; then
    journalctl --since "$journal_since" --no-pager >"$WORK_DIR/journalctl.log" 2>/dev/null || true
  else
    journalctl --no-pager >"$WORK_DIR/journalctl.log" 2>/dev/null || true
  fi
  ENTRIES=$((ENTRIES + 1))
fi

if [[ -f /var/log/syslog ]]; then
  cp /var/log/syslog "$WORK_DIR"/syslog 2>/dev/null || true
  ENTRIES=$((ENTRIES + 1))
elif [[ -f /var/log/messages ]]; then
  cp /var/log/messages "$WORK_DIR"/messages 2>/dev/null || true
  ENTRIES=$((ENTRIES + 1))
fi

echo "$extra_paths_json" | jq -r '.[]?' | while read -r path; do
  include_file "$path"
done

tar -czf "$ARTIFACT" -C "$WORK_DIR" . >/dev/null 2>&1 || true
OUTPUT_DATA=$(jq -n --arg path "$ARTIFACT" --argjson count $ENTRIES '{artifact_path: $path, entries_collected: $count}')
rune_ok "logs archived" "$OUTPUT_DATA"
