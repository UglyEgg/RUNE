#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
. "${SCRIPT_DIR}/lib/rune_bpcs.sh"

rune_init
CHECK_JOBS=$(rune_param "check_jobs" "false")

SERVICE_STATE="simulated"
JOB_SUMMARY=""

if command -v systemctl >/dev/null 2>&1 && systemctl list-unit-files nomad.service >/dev/null 2>&1; then
  if systemctl restart nomad >/dev/null 2>&1; then
    SERVICE_STATE=$(systemctl is-active nomad 2>/dev/null || echo "unknown")
  else
    rune_error 1 "systemctl restart nomad failed"
  fi
fi

if [[ "$CHECK_JOBS" == "true" ]] && command -v nomad >/dev/null 2>&1; then
  JOB_SUMMARY=$(nomad job status 2>/dev/null | head -n 5 | tr -s ' ')
fi

OUTPUT_DATA=$(jq -n --arg state "$SERVICE_STATE" --arg jobs "$JOB_SUMMARY" '{service_state: $state, job_status: $jobs}')
rune_ok "nomad restart completed" "$OUTPUT_DATA"
