# Shared Bash Plugin Communication Specification (BPCS) helper library.
# Source this file from your RUNE Bash plugin:
#   source "/path/to/rune_bpcs.sh"
#
# Requirements:
# - bash
# - jq
#
# This library supports:
# - Easy mode: rune_ok / rune_error / rune_finish generate full BPCS output
# - Advanced mode: build your own BPCS JSON and call rune_emit

# Global state populated during initialization (rune_init).
RUNE_INPUT_JSON=""
RUNE_MESSAGE_METADATA="{}"
RUNE_OBSERVABILITY="{}"
RUNE_INPUT_PARAMETERS_JSON="{}"
RUNE_CONTEXT_JSON="{}"

# Output accumulator state for rune_out / rune_err / rune_finish.
RUNE_OUT_FIELDS=()
RUNE_ERROR_CODE=0
RUNE_ERROR_MESSAGE=""

# -----------------------
# Internal helpers
# -----------------------

_rune_require_jq() {
  if ! command -v jq >/dev/null 2>&1; then
    echo "jq is required for rune_bpcs.sh" >&2
    exit 2
  fi
}

_rune_now_iso8601_utc() {
  # Best effort ISO 8601 UTC timestamp.
  # GNU date supports %3N. If it fails, fall back to seconds precision.
  local ts
  ts=$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ" 2>/dev/null) || ts=""
  if [[ -z "$ts" ]]; then
    ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null) || ts="1970-01-01T00:00:00Z"
  fi
  printf '%s' "$ts"
}

_rune_uuid() {
  if command -v uuidgen >/dev/null 2>&1; then
    uuidgen
    return 0
  fi
  if [[ -r /proc/sys/kernel/random/uuid ]]; then
    cat /proc/sys/kernel/random/uuid
    return 0
  fi
  # Fallback: not a real UUID, but unique enough for local testing.
  printf 'rune-%s-%s-%s' "$(date -u +%s 2>/dev/null || echo 0)" "$$" "${RANDOM:-0}"
}

_rune_compact_json() {
  # Compact and validate JSON. Exits non-zero if invalid.
  jq -ce '.'
}

_rune_safe_json_object() {
  # Ensure the candidate is a JSON object. If invalid or not an object, return fallback (object).
  local candidate="$1"
  local fallback="$2"
  if [[ -z "$candidate" ]]; then
    candidate="$fallback"
  fi
  if echo "$candidate" | jq -e 'type=="object"' >/dev/null 2>&1; then
    echo "$candidate" | jq -c '.'
  else
    echo "$fallback" | jq -c '.'
  fi
}

_rune_safe_json_any() {
  # Ensure candidate is valid JSON. If invalid, return fallback (any JSON).
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

_rune_emit_bootstrap_error() {
  # Emit a BPCS error using generated metadata/observability.
  local code="$1"
  local message="$2"
  local details_json
  if [[ "$#" -ge 3 ]]; then
    details_json="$3"
  else
    details_json="{}"
  fi
  local details
  details=$(_rune_safe_json_object "$details_json" "{}")

  local now id trace span
  now=$(_rune_now_iso8601_utc)
  id=$(_rune_uuid)
  trace="trace-$id"
  span="span-$id"

  jq -nc \
    --arg now "$now" \
    --arg id "$id" \
    --arg trace "$trace" \
    --arg span "$span" \
    --arg msg "$message" \
    --argjson details "$details" \
    --argjson code "$code" \
    '{
      message_metadata: {version:"1.0", message_id:$id, created_at:$now},
      payload: null,
      observability: {trace_id:$trace, span_id:$span},
      error: {code: ($code|tonumber), message: $msg, details: $details}
    }'
  exit "$code"
}

_rune_validate_bpcs_output() {
  # Validate that stdin is a BPCS output message.
  # Returns 0 if valid, 1 otherwise.
  jq -e '
    type=="object"
    and (.message_metadata|type=="object")
    and (.message_metadata.version|type=="string")
    and (.message_metadata.message_id|type=="string")
    and (.message_metadata.created_at|type=="string")
    and (has("payload"))
    and (has("observability"))
    and (.observability|type=="object")
    and (.observability.trace_id|type=="string")
    and (.observability.span_id|type=="string")
    and (has("error"))
    and (
      if .error == null then
        (.payload|type=="object")
        and (.payload.result=="success")
        and (.payload.output_data|type=="object")
      else
        (.payload == null)
        and (.error|type=="object")
        and (.error.code|type=="number")
        and (.error.message|type=="string")
        and (.error.details|type=="object")
      end
    )
  ' >/dev/null 2>&1
}

# -----------------------
# Public API
# -----------------------

rune_init() {
  _rune_require_jq

  if [[ -n "$RUNE_INPUT_JSON" ]]; then
    return 0
  fi

  local raw
  raw=$(cat)

  if [[ -z "${raw}" ]]; then
    _rune_emit_bootstrap_error 1 "Invalid input: empty stdin" '{"reason":"stdin was empty"}'
  fi

  # Validate JSON and require an object at the top level.
  if ! echo "$raw" | jq -e 'type=="object"' >/dev/null 2>&1; then
    _rune_emit_bootstrap_error 1 "Invalid input: expected a JSON object" '{"reason":"stdin was not valid JSON object"}'
  fi

  RUNE_INPUT_JSON=$(echo "$raw" | jq -c '.')

  # Extract and normalize message_metadata.
  local now gen_id
  now=$(_rune_now_iso8601_utc)
  gen_id=$(_rune_uuid)

  RUNE_MESSAGE_METADATA=$(
    echo "$RUNE_INPUT_JSON" | jq -c \
      --arg now "$now" \
      --arg gen_id "$gen_id" \
      '(.message_metadata // {})
       | (if type!="object" then {} else . end)
       | .version = (.version // "1.0")
       | .message_id = (.message_id // $gen_id)
       | .created_at = (.created_at // $now)'
  )

  # Extract and normalize observability.
  RUNE_OBSERVABILITY=$(
    echo "$RUNE_INPUT_JSON" | jq -c \
      --arg gen_id "$gen_id" \
      '(.observability // {})
       | (if type!="object" then {} else . end)
       | .trace_id = (.trace_id // ("trace-" + $gen_id))
       | .span_id  = (.span_id  // ("span-"  + $gen_id))'
  )

  # Extract payload.input_parameters and payload.context.
  RUNE_INPUT_PARAMETERS_JSON=$(_rune_safe_json_object "$(echo "$RUNE_INPUT_JSON" | jq -c '.payload.input_parameters // {}')" "{}")
  RUNE_CONTEXT_JSON=$(_rune_safe_json_object "$(echo "$RUNE_INPUT_JSON" | jq -c '.payload.context // {}')" "{}")
}

# Return a parameter as a string. Objects/arrays are returned as compact JSON text.
rune_param() {
  local key="$1"
  local default_value="${2-}"
  echo "$RUNE_INPUT_JSON" | jq -r --arg key "$key" --arg dflt "$default_value" '
    (.payload.input_parameters[$key] // $dflt)
    | if type=="object" or type=="array" then tojson
      elif type=="boolean" then (if . then "true" else "false" end)
      elif type=="number" then tostring
      else .
      end
  '
}

# Return a parameter as JSON (compact). default_json must be valid JSON (e.g. "null", "{}", "[]", "\"text\"").
rune_param_json() {
  local key="$1"
  local default_json="${2:-null}"
  echo "$RUNE_INPUT_JSON" | jq -c --arg key "$key" --argjson dflt "$default_json" '(.payload.input_parameters[$key] // $dflt)'
}

rune_all_params() {
  echo "$RUNE_INPUT_PARAMETERS_JSON"
}

# Return a context value as a string. Objects/arrays are returned as compact JSON text.
rune_ctx() {
  local key="$1"
  local default_value="${2-}"
  echo "$RUNE_INPUT_JSON" | jq -r --arg key "$key" --arg dflt "$default_value" '
    (.payload.context[$key] // $dflt)
    | if type=="object" or type=="array" then tojson
      elif type=="boolean" then (if . then "true" else "false" end)
      elif type=="number" then tostring
      else .
      end
  '
}

# Return a context value as JSON (compact).
rune_ctx_json() {
  local key="$1"
  local default_json="${2:-null}"
  echo "$RUNE_INPUT_JSON" | jq -c --arg key "$key" --argjson dflt "$default_json" '(.payload.context[$key] // $dflt)'
}

rune_all_ctx() {
  echo "$RUNE_CONTEXT_JSON"
}

# Access message_metadata (and fall back to observability for convenience).
rune_meta() {
  local key="$1"
  local default_value="${2-}"

  local v
  v=$(echo "$RUNE_MESSAGE_METADATA" | jq -r --arg key "$key" 'if has($key) then .[$key] else empty end')
  if [[ -n "$v" && "$v" != "null" ]]; then
    echo "$v"
    return 0
  fi

  v=$(echo "$RUNE_OBSERVABILITY" | jq -r --arg key "$key" 'if has($key) then .[$key] else empty end')
  if [[ -n "$v" && "$v" != "null" ]]; then
    echo "$v"
    return 0
  fi

  echo "$default_value"
}

# Access observability.
rune_obs() {
  local key="$1"
  local default_value="${2-}"
  echo "$RUNE_OBSERVABILITY" | jq -r --arg key "$key" --arg dflt "$default_value" '.[$key] // $dflt'
}

# Emit a BPCS success message and exit 0.
# The status message (arg1) is injected into output_data.message if that key is not already present.
rune_ok() {
  local status_message="$1"
  local output_json
  if [[ "$#" -ge 2 ]]; then
    output_json="$2"
  else
    output_json="{}"
  fi

  local output_data
  output_data=$(_rune_safe_json_object "$output_json" "{}")

  jq -nc \
    --argjson mm "$RUNE_MESSAGE_METADATA" \
    --argjson obs "$RUNE_OBSERVABILITY" \
    --arg msg "$status_message" \
    --argjson data "$output_data" \
    '{
      message_metadata: $mm,
      payload: {
        result: "success",
        output_data: (
          if ($msg != "" and ($data|has("message")|not)) then
            ($data + {message:$msg})
          else
            $data
          end
        )
      },
      observability: $obs,
      error: null
    }'
  exit 0
}

# Emit a BPCS error message and exit with the provided code.
# details_json must be an object; invalid values are replaced with {}.
rune_error() {
  local code="$1"
  local message="$2"
  local details_json
  if [[ "$#" -ge 3 ]]; then
    details_json="$3"
  else
    details_json="{}"
  fi

  local details
  details=$(_rune_safe_json_object "$details_json" "{}")

  jq -nc \
    --argjson mm "$RUNE_MESSAGE_METADATA" \
    --argjson obs "$RUNE_OBSERVABILITY" \
    --arg msg "$message" \
    --argjson details "$details" \
    --argjson code "$code" \
    '{
      message_metadata: $mm,
      payload: null,
      observability: $obs,
      error: {code: ($code|tonumber), message: $msg, details: $details}
    }'
  exit "$code"
}

# Alias for common wording in docs and scripts.
rune_fail() { rune_error "$@"; }

# Internal: build a JSON object from key=value pairs (all values become strings).
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

    [ -z "$key" ] && continue

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

# Success helper that builds payload.output_data from key=value pairs and delegates to rune_ok.
rune_ok_kv() {
  local message="$1"
  shift || true
  local output_data_json
  output_data_json=$(_rune_build_kv_json "$@")
  rune_ok "$message" "$output_data_json"
}

# Error helper that builds error.details from key=value pairs and delegates to rune_error.
rune_error_kv() {
  local code="$1"
  local message="$2"
  shift 2 || true
  local details_json
  details_json=$(_rune_build_kv_json "$@")
  rune_error "$code" "$message" "$details_json"
}
rune_fail_kv() { rune_error_kv "$@"; }

# Record an output field (string value).
rune_out() {
  local pair
  case "$#" in
    1) pair="$1" ;;
    2) pair="$1=$2" ;;
    *) echo "rune_out expects KEY=VALUE or KEY VALUE" >&2; return 1 ;;
  esac
  RUNE_OUT_FIELDS+=("$pair")
}

# Record an error to be emitted later by rune_finish.
rune_err() {
  if [ "$#" -lt 1 ]; then
    echo "rune_err expects at least an error code" >&2
    return 1
  fi

  RUNE_ERROR_CODE="$1"
  shift || true

  if [ "$#" -gt 0 ]; then
    RUNE_ERROR_MESSAGE="$*"
  else
    RUNE_ERROR_MESSAGE="error"
  fi
}

# Finalize the plugin and exit:
# - If an error was recorded, emit rune_error(code, message, details_from_rune_out)
# - Otherwise, emit rune_ok(success_message, output_data_from_rune_out)
rune_finish() {
  local success_message="${1:-success}"
  local data_json
  data_json=$(_rune_build_kv_json "${RUNE_OUT_FIELDS[@]}")

  if [ "${RUNE_ERROR_CODE}" -ne 0 ]; then
    local msg="${RUNE_ERROR_MESSAGE:-error}"
    rune_error "${RUNE_ERROR_CODE}" "$msg" "$data_json"
  else
    rune_ok "$success_message" "$data_json"
  fi
}

# Advanced mode: emit a fully formed BPCS JSON message.
# If exit_code is omitted:
# - success => 0
# - error   => .error.code (or 100)
rune_emit() {
  _rune_require_jq

  local json="$1"
  local exit_code="${2-}"

  local compact
  compact=$(echo "$json" | _rune_compact_json) || {
    echo "rune_emit: output is not valid JSON" >&2
    exit 2
  }

  if ! echo "$compact" | _rune_validate_bpcs_output; then
    echo "rune_emit: output is not valid BPCS output" >&2
    exit 2
  fi

  echo "$compact"

  if [[ -z "$exit_code" ]]; then
    exit_code=$(echo "$compact" | jq -r 'if .error==null then 0 else (.error.code // 100) end')
  fi

  exit "$exit_code"
}
