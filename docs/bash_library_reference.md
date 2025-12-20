# RUNE Bash Plugin Guide (BPCS)

This guide explains how to write Bash plugins that can be executed by the RUNE framework using the Bash Plugin Communication Specification (BPCS).

If you can write a shell script and you can survive `jq`, you are qualified.

## The rules that matter

1. **Your plugin reads exactly one JSON object from stdin.**
2. **Your plugin writes exactly one JSON object to stdout.**
3. **Everything else goes to stderr.**
4. **Your exit code must match the outcome.**
5. **Never print secrets.**

RUNE (via the Local Mediation Module) treats stdout as the machine contract. If you print anything other than the final JSON to stdout, you will break the contract.

## Required dependency

- `jq` is required. This is non negotiable if you want reliable JSON handling.

## BPCS message shapes

### Input message (stdin)

Your plugin receives a single JSON object with these top level keys:

- `message_metadata` (object)
- `payload` (object)
- `observability` (object)

`payload` includes:

- `input_parameters` (object): the arguments to your plugin
- `context` (object): shared request context from RUNE

Example:

```json
{
  "message_metadata": {
    "version": "1.0",
    "message_id": "mid-123",
    "correlation_id": "corr-abc",
    "created_at": "2025-12-20T12:00:00.000Z"
  },
  "payload": {
    "input_parameters": {
      "service": "sshd",
      "restart": true
    },
    "context": {
      "node": "venger",
      "requested_by": "rich"
    }
  },
  "observability": {
    "trace_id": "trace-1",
    "span_id": "span-1"
  }
}
```

### Output message (stdout)

Your plugin must emit a single JSON object with these top level keys:

- `message_metadata` (object)
- `payload` (object or null)
- `observability` (object)
- `error` (object or null)

Success output:

```json
{
  "message_metadata": { "...": "..." },
  "payload": {
    "result": "success",
    "output_data": { "...": "..." }
  },
  "observability": { "...": "..." },
  "error": null
}
```

Error output:

```json
{
  "message_metadata": { "...": "..." },
  "payload": null,
  "observability": { "...": "..." },
  "error": {
    "code": 2,
    "message": "Resource not found",
    "details": { "...": "..." }
  }
}
```

## Standard exit codes and error codes

Bash exit codes are 0 to 255. BPCS standard codes stay safely inside that range.

Use these codes consistently:

- `0` success
- `1` validation error (bad input)
- `2` resource or dependency error (file missing, network failure, command unavailable)
- `3` business logic failure (the action ran, but failed to do the intended thing)
- `4` configuration error (missing env var, missing config, wrong OS assumption)
- `100` unhandled exception or system error (unexpected fatal conditions)

In this library, **the exit code is the same as `error.code`** on failures.

## Using the shared library

RUNE provides `rune_bpcs.sh` as a shared library. Your plugin should source it and then call `rune_init` immediately.

### Minimal plugin template (easy mode)

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
source "${SCRIPT_DIR}/rune_bpcs.sh"

rune_init

SERVICE="$(rune_param service "")"
if [[ -z "${SERVICE}" ]]; then
  rune_error 1 "Missing required parameter: service" '{"missing":["service"]}'
fi

# Do the work
if systemctl restart "${SERVICE}" 2>/dev/null; then
  OUT="$(jq -nc --arg svc "${SERVICE}" '{service:$svc, restarted:true}')"
  rune_ok "Service restarted" "${OUT}"
else
  DETAILS="$(jq -nc --arg svc "${SERVICE}" '{service:$svc, restarted:false}')"
  rune_error 2 "Failed to restart service" "${DETAILS}"
fi
```

### Reading input

#### Parameters

- `rune_param KEY DEFAULT`  
  Returns a parameter as a string.

- `rune_param_json KEY DEFAULT_JSON`  
  Returns a parameter as JSON.

- `rune_all_params`  
  Returns the full `input_parameters` object as JSON.

Examples:

```bash
SERVICE="$(rune_param service "")"
RESTART="$(rune_param restart "false")"           # "true" or "false"
RAW_PARAMS_JSON="$(rune_all_params)"              # JSON object string
```

#### Context

- `rune_ctx KEY DEFAULT`
- `rune_ctx_json KEY DEFAULT_JSON`
- `rune_all_ctx`

Examples:

```bash
NODE="$(rune_ctx node "unknown")"
CTX_JSON="$(rune_all_ctx)"
```

#### Metadata and observability

- `rune_meta KEY DEFAULT`  
  Looks up the key in `message_metadata`, then falls back to `observability`.

- `rune_obs KEY DEFAULT`  
  Looks up the key only in `observability`.

Examples:

```bash
MESSAGE_ID="$(rune_meta message_id "")"
TRACE_ID="$(rune_meta trace_id "none")"   # works via fallback
SPAN_ID="$(rune_obs span_id "none")"
```

### Writing output

#### `rune_ok MESSAGE OUTPUT_DATA_JSON`

Emits a full BPCS success message and exits `0`.

`OUTPUT_DATA_JSON` must be a JSON object string. Use `jq -nc` to build it safely.

Note: `MESSAGE` is injected into `output_data.message` only if you did not already provide a `message` key.

#### `rune_error CODE MESSAGE DETAILS_JSON`

Emits a full BPCS error message and exits `CODE`.

`DETAILS_JSON` must be a JSON object string. Use `jq -nc` to build it safely.

#### Convenience helpers

If you prefer simple key value output without thinking about JSON types:

- `rune_ok_kv "message" "key=value" "key2=value2"`
- `rune_error_kv 2 "message" "key=value"`

All values become strings in these helpers.

#### Accumulator style

For longer scripts, you can accumulate output fields and finish once:

```bash
rune_out "service=$SERVICE"
rune_out "attempted_restart=true"

if ! systemctl restart "$SERVICE"; then
  rune_err 2 "Restart failed"
fi

rune_finish "completed"
```

- If no error was recorded, `rune_finish` emits success.
- If an error was recorded, `rune_finish` emits error using the accumulated output as `error.details`.

### Advanced mode

If you want full control, build the entire BPCS output JSON yourself and then call `rune_emit`.

This is useful when:
- you already have a full JSON response constructed
- you need to emit a very specific output shape
- you want to validate that your response is BPCS compliant before printing it

Example:

```bash
OUT="$(jq -nc '{something:"custom"}')"

RESP="$(jq -nc \
  --argjson mm "${RUNE_MESSAGE_METADATA}" \
  --argjson obs "${RUNE_OBSERVABILITY}" \
  --argjson out "${OUT}" \
  '{
    message_metadata: $mm,
    payload: {result:"success", output_data:$out},
    observability: $obs,
    error: null
  }'
)"

rune_emit "${RESP}" 0
```

`rune_emit` validates the JSON is BPCS compliant, prints it, and exits.

## Testing locally

Create an input file:

```bash
cat > input.json <<'JSON'
{
  "message_metadata": {
    "version": "1.0",
    "message_id": "mid-test",
    "created_at": "2025-12-20T12:00:00Z"
  },
  "payload": {
    "input_parameters": { "mode": "easy" },
    "context": { "node": "local" }
  },
  "observability": {
    "trace_id": "trace-test",
    "span_id": "span-test"
  }
}
JSON
```

Run the plugin:

```bash
cat input.json | ./noop.sh | jq
echo "exit=$?"
```

To force an error response in the provided noop test plugin:

```bash
cat input.json | jq '.payload.input_parameters.fail="true"' | ./noop.sh | jq
echo "exit=$?"
```

## Common failure modes

- Printing debug output to stdout instead of stderr
- Forgetting `rune_init`
- Building JSON by string concatenation instead of `jq`
- Returning non JSON on error paths
- Exiting non zero without emitting a BPCS error message
- Putting arrays or objects into `rune_ok_kv` and expecting them to stay typed (they become strings)

## Quick checklist

- [ ] `source rune_bpcs.sh`
- [ ] `rune_init` is called before you read parameters
- [ ] stdout contains exactly one JSON object at the end
- [ ] stderr contains any diagnostics
- [ ] success uses exit 0
- [ ] failures use an `error` object and non zero exit code

