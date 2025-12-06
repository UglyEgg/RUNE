# Bash Plugin Communication Specification (BPCS)

## Purpose

BPCS defines how Bash plugins receive data from RUNE and return structured results. It provides a simple API through a shared Bash library so that plugin authors do not need to manage JSON formatting, parsing, or protocol details.

## Plugin Data Flow

1. RUNE builds an RCS message.
2. RUNE sends JSON to the plugin's stdin.
3. Plugin reads parameters through the shared library.
4. Plugin executes logic.
5. Plugin returns JSON through the shared library.
6. Plugin exits with a meaningful exit code.

## Shared Library

The shared library (rune_bpcs.sh) handles:

- Reading and parsing stdin JSON.
- Retrieving input parameters.
- Retrieving metadata such as node or trace id.
- Emitting success or error JSON messages.
- Managing structured exit codes.

Plugins source the library:

```bash
. /opt/rune/lib/rune_bpcs.sh
rune_init
```

## Input Structure (stdin)

Plugins receive a trimmed version of RCS:

```json
{
  "message_metadata": {
    "trace_id": "e3a2b5...",
    "action": "restart-docker",
    "node": "web01"
  },
  "payload": {
    "schema_version": "rcs_v1",
    "data": {
      "input_parameters": {
        "force": true,
        "timeout": 30
      }
    }
  }
}
```

## Output Structure (stdout)

Plugins must emit exactly one JSON object.

### Success

```json
{
  "payload": {
    "result": "success",
    "output_data": {
      "message": "Docker restarted",
      "service": "docker"
    }
  },
  "error": null
}
```

### Error

```json
{
  "payload": null,
  "error": {
    "code": 1001,
    "message": "Failed to restart Docker",
    "data": {
      "exit_code": 1
    }
  }
}
```

## Exit Codes

- 0 indicates success.
- Non zero indicates failure.
- Plugins should use the shared library's rune_error function.

## Library API

### rune_init

Reads stdin, parses JSON, initializes library state.

### rune_param KEY DEFAULT

Retrieves an input parameter.

### rune_meta KEY DEFAULT

Retrieves metadata such as action or node.

### rune_ok MESSAGE JSON_DATA

Writes success JSON and exits 0.

### rune_error CODE MESSAGE JSON_DATA

Writes structured error JSON and exits CODE.

## Example Plugin

```bash
#!/bin/bash
set -euo pipefail
. /opt/rune/lib/rune_bpcs.sh
rune_init

SERVICE=$(rune_param "service" "docker")

if systemctl restart "$SERVICE"; then
  rune_ok "Service restarted" '{"service": "'"$SERVICE"'"}'
else
  rune_error 2001 "Restart failed" '{"service": "'"$SERVICE"'"}'
fi
```

## Rules

- stdout is reserved for the final JSON output only.
- stderr may contain diagnostic logs.
- If a plugin fails without valid JSON, the Mediator will wrap it in an EPS message.

© 2025 Richard Majewski. Licensed under the MPL-2.0.
