#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
. "${SCRIPT_DIR}/lib/rune_bpcs.sh"

rune_init

SERVICE_STATE="simulated"
if command -v systemctl >/dev/null 2>&1 && systemctl list-unit-files docker.service >/dev/null 2>&1; then
  if systemctl restart docker >/dev/null 2>&1; then
    SERVICE_STATE=$(systemctl is-active docker 2>/dev/null || echo "unknown")
  else
    rune_error 1 "systemctl restart docker failed"
  fi
fi

OUTPUT_DATA=$(jq -n --arg state "$SERVICE_STATE" '{service_state: $state}')
rune_ok "docker restart completed" "$OUTPUT_DATA"
