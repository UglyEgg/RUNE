#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

# Prefer a colocated library, but support the common ./lib layout.
if [[ -f "${SCRIPT_DIR}/rune_bpcs.sh" ]]; then
  # shellcheck source=/dev/null
  source "${SCRIPT_DIR}/rune_bpcs.sh"
elif [[ -f "${SCRIPT_DIR}/lib/rune_bpcs.sh" ]]; then
  # shellcheck source=/dev/null
  source "${SCRIPT_DIR}/lib/rune_bpcs.sh"
else
  echo "noop.sh: could not locate rune_bpcs.sh" >&2
  exit 2
fi

rune_init

# Parameters for testing:
# - mode: "easy" (default) or "advanced"
# - fail: "true" to force an error response
MODE="$(rune_param mode "easy")"
FAIL="$(rune_param fail "false")"

PARAMS_JSON="$(rune_all_params)"
CTX_JSON="$(rune_all_ctx)"

TRACE_ID="$(rune_obs trace_id "unknown")"
SPAN_ID="$(rune_obs span_id "unknown")"
MESSAGE_ID="$(rune_meta message_id "")"
CORRELATION_ID="$(rune_meta correlation_id "")"

if [[ "${FAIL}" == "true" ]]; then
  DETAILS="$(jq -nc --arg mode "${MODE}" --argjson params "${PARAMS_JSON}" --argjson ctx "${CTX_JSON}" '{action:"noop", mode:$mode, input_parameters:$params, context:$ctx, reason:"forced failure for testing"}')"
  if [[ "${MODE}" == "advanced" ]]; then
    RESP="$(jq -nc --argjson mm "${RUNE_MESSAGE_METADATA}" --argjson obs "${RUNE_OBSERVABILITY}" --argjson details "${DETAILS}" '{message_metadata:$mm, payload:null, observability:$obs, error:{code:3, message:"Forced failure", details:$details}}')"
    rune_emit "${RESP}"
  else
    rune_error 3 "Forced failure" "${DETAILS}"
  fi
fi

OUTPUT_DATA="$(jq -nc \
  --arg mode "${MODE}" \
  --argjson params "${PARAMS_JSON}" \
  --argjson ctx "${CTX_JSON}" \
  --arg trace_id "${TRACE_ID}" \
  --arg span_id "${SPAN_ID}" \
  --arg message_id "${MESSAGE_ID}" \
  --arg correlation_id "${CORRELATION_ID}" \
  '{
    action: "noop",
    mode: $mode,
    input_parameters: $params,
    context: $ctx,
    echo: {
      message_id: $message_id,
      correlation_id: $correlation_id,
      trace_id: $trace_id,
      span_id: $span_id
    }
  }'
)"

if [[ "${MODE}" == "advanced" ]]; then
  # Advanced mode: construct full BPCS output yourself, then emit it.
  RESP="$(jq -nc --argjson mm "${RUNE_MESSAGE_METADATA}" --argjson obs "${RUNE_OBSERVABILITY}" --argjson out "${OUTPUT_DATA}" '{message_metadata:$mm, payload:{result:"success", output_data:$out}, observability:$obs, error:null}')"
  rune_emit "${RESP}" 0
else
  # Easy mode: library constructs the full BPCS output (and injects a message into output_data.message).
  rune_ok "noop executed" "${OUTPUT_DATA}"
fi
