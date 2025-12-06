#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
. "${SCRIPT_DIR}/lib/rune_bpcs.sh"

rune_init
PARAMS_JSON=$(rune_all_params)
OUTPUT_DATA=$(jq -n --argjson params "$PARAMS_JSON" '{action: "noop", input_parameters: $params}')
rune_ok "noop executed" "$OUTPUT_DATA"
