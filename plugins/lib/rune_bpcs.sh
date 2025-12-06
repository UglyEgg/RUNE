# Shared Bash Plugin Communication Specification (BPCS) helper library.
# Handles input parsing and structured output for RUNE plugins.

# Global state populated during initialization.
RUNE_INPUT_JSON=""
RUNE_MESSAGE_METADATA="{}"
RUNE_OBSERVABILITY="{}"
RUNE_ROUTING="{}"
RUNE_PARAMS_JSON="{}"
# Output accumulator state for rune_out / rune_err / rune_finish.
RUNE_OUT_FIELDS=()
RUNE_ERROR_CODE=0
RUNE_ERROR_MESSAGE=""

_rune_require_jq() {
  if ! command -v jq >/dev/null 2>&1; then
    echo "jq is required for rune_bpcs.sh" >&2
    exit 2
  fi
}

_rune_safe_json() {
  local candidate="$1"
  local fallback="$2"
  if [[ -z "$candidate" ]]; then
    candidate="$fallback"
  fi
  if echo "$candidate" | jq -e . >/dev/null 2>&1; then
    echo "$candidate" | jq -c '.'
  else
    echo "$fallback" | jq -c '.'
  fi
}

_rune_read_input() {
  if [[ -n "$RUNE_INPUT_JSON" ]]; then
    return
  fi
  RUNE_INPUT_JSON=$(cat)
  if [[ -z "$RUNE_INPUT_JSON" ]]; then
    echo "No input provided to plugin" >&2
    exit 2
  fi
}

rune_init() {
  _rune_require_jq
  _rune_read_input
  RUNE_MESSAGE_METADATA=$(_rune_safe_json "$(echo "$RUNE_INPUT_JSON" | jq -c '.message_metadata // {}')" "{}")
  RUNE_OBSERVABILITY=$(_rune_safe_json "$(echo "$RUNE_INPUT_JSON" | jq -c '.observability // {}')" "{}")
  RUNE_ROUTING=$(_rune_safe_json "$(echo "$RUNE_INPUT_JSON" | jq -c '.routing // {}')" "{}")
  RUNE_PARAMS_JSON=$(_rune_safe_json "$(echo "$RUNE_INPUT_JSON" | jq -c '.payload.data.input_parameters // {}')" "{}")
}

rune_param() {
  local key="$1"
  local default_value="${2-}"
  local value
  value=$(echo "$RUNE_INPUT_JSON" |
    jq -r --arg key "$key" --arg def "$default_value" '(.payload.data.input_parameters[$key] // $def) | (if type == "boolean" then (if . then "true" else "false" end) elif type == "number" then tostring else . end)')
  echo "$value"
}

rune_param_json() {
  local key="$1"
  local default_json="${2:-null}"
  local result
  result=$(echo "$RUNE_INPUT_JSON" |
    jq -c --arg key "$key" --argjson def "$default_json" '(.payload.data.input_parameters[$key] // $def)') || result="$default_json"
  echo "$result"
}

rune_all_params() {
  echo "$RUNE_PARAMS_JSON"
}

rune_meta() {
  local key="$1"
  local default_value="${2-}"
  local value
  value=$(echo "$RUNE_MESSAGE_METADATA" | jq -r --arg key "$key" --arg def "$default_value" '.[$key] // $def')
  echo "$value"
}

rune_ok() {
  local message="$1"
  local output_json="$2"
  local output_data
  output_data=$(_rune_safe_json "$output_json" "{}")
  jq -nc \
    --argjson mm "$RUNE_MESSAGE_METADATA" \
    --argjson obs "$RUNE_OBSERVABILITY" \
    --argjson routing "$RUNE_ROUTING" \
    --arg message "$message" \
    --argjson data "$output_data" \
    '{message_metadata: $mm, observability: $obs, routing: $routing, payload: {result: "success", message: $message, output_data: $data}, error: null}'
  exit 0
}

rune_error() {
  local code="$1"
  local message="$2"
  local error_data_json="${3:-null}"
  local error_data
  error_data=$(_rune_safe_json "$error_data_json" "null")
  jq -nc \
    --argjson mm "$RUNE_MESSAGE_METADATA" \
    --argjson obs "$RUNE_OBSERVABILITY" \
    --argjson routing "$RUNE_ROUTING" \
    --arg message "$message" \
    --argjson data "$error_data" \
    --argjson code "$code" \
    '{message_metadata: $mm, observability: $obs, routing: $routing, payload: {result: "error", output_data: ($data // {})}, error: {code: ($code|tonumber), message: $message, data: $data}}'
  exit "$code"
}

# Internal: build a JSON object from key=value pairs.
# All values are encoded as strings. For more complex output,
# plugins can still call rune_ok / rune_error directly with
# pre-built JSON.
_rune_build_kv_json() {
  if [ "$#" -eq 0 ]; then
    printf '{}\n'
    return 0
  fi

  local jq_args=(jq -n)
  local jq_prog='{'
  local first=1
  local pair key val

  for pair in "$@"; do
    key=${pair%%=*}
    val=${pair#*=}

    # Skip if key is empty
    [ -z "$key" ] && continue

    # Keys should be identifier-like (letters, numbers, underscore).
    jq_args+=(--arg "$key" "$val")

    if [ $first -eq 0 ]; then
      jq_prog+=', '
    else
      first=0
    fi

    jq_prog+="\"$key\": \$$key"
  done

  jq_prog+='}'
  "${jq_args[@]}" "$jq_prog"
}

# Success helper that builds payload.output_data from key=value pairs
# and delegates to rune_ok.
#
# Usage:
#   rune_ok_kv "logs archived" \\
#     "artifact_path=$ARTIFACT" \\
#     "entries_collected=$ENTRIES"
rune_ok_kv() {
  local message="$1"
  shift || true

  local output_data_json
  output_data_json=$(_rune_build_kv_json "$@")

  rune_ok "$message" "$output_data_json"
}

# Error helper that builds error.data from key=value pairs
# and delegates to rune_error.
#
# Usage:
#   rune_error_kv 2001 "Failed to restart service" \\
#     "service=$SERVICE" \\
#     "node=$NODE"
rune_error_kv() {
  local code="$1"
  local message="$2"
  shift 2 || true

  local error_data_json
  error_data_json=$(_rune_build_kv_json "$@")

  rune_error "$code" "$message" "$error_data_json"
}

# Record an output field, similar to "echo key=value" but structured.
#
# Usage:
#   rune_out "artifact_path=$ARTIFACT"
#   rune_out "entries_collected=$ENTRIES"
#   rune_out message "logs archived successfully"
rune_out() {
  local pair

  case "$#" in
  1)
    pair="$1"
    ;;
  2)
    pair="$1=$2"
    ;;
  *)
    echo "rune_out expects KEY=VALUE or KEY VALUE" >&2
    return 1
    ;;
  esac

  RUNE_OUT_FIELDS+=("$pair")
}

# Record that an error occurred. This does not exit immediately;
# rune_finish will decide whether to send success or error.
#
# Usage:
#   rune_err 2001 "Failed to restart service"
rune_err() {
  if [ "$#" -lt 1 ]; then
    echo "rune_err expects at least an error code" >&2
    return 1
  fi

  RUNE_ERROR_CODE="$1"
  shift

  if [ "$#" -gt 0 ]; then
    RUNE_ERROR_MESSAGE="$*"
  else
    RUNE_ERROR_MESSAGE="error"
  fi
}

# Finalize the plugin:
# - If an error was recorded (RUNE_ERROR_CODE != 0), send an error.
# - Otherwise, send a success.
#
# Usage:
#   rune_finish              # default success message "success"
#   rune_finish "completed"  # custom success message
#
# NOTE: This will not return; it calls rune_ok / rune_error,
# which both exit the script.
rune_finish() {
  local success_message="${1:-success}"

  # Build a JSON object from all recorded rune_out fields
  local data_json
  data_json=$(_rune_build_kv_json "${RUNE_OUT_FIELDS[@]}")

  if [ "$RUNE_ERROR_CODE" -ne 0 ]; then
    local message="${RUNE_ERROR_MESSAGE:-error}"
    rune_error "$RUNE_ERROR_CODE" "$message" "$data_json"
  else
    rune_ok "$success_message" "$data_json"
  fi
}
