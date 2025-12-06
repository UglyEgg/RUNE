# Plugin Development Guide for RUNE

This guide explains how to create, test, and register Bash- or Python-based plugins for RUNE's MVP framework.

---

## Plugin Overview

Plugins are standalone scripts executed on remote systems via SSH or SSM. Each plugin performs a discrete action (e.g., gather logs, restart a service) and must conform to RUNE’s **Bash Plugin Communication Spec (BPCS)** by reading structured JSON from stdin and returning structured JSON to stdout.

Supported languages:

- ✅ Bash (primary for MVP)
- ⬜️ Python (planned)

---

## Plugin Structure (Bash Example)

```bash
#!/bin/bash
set -euo pipefail

# Read stdin into a variable
INPUT=$(cat)

# Extract data (example using jq)
PARAMS=$(echo "$INPUT" | jq -r '.payload.data.input_parameters')
HOSTNAME=$(hostname)

# Main logic (example: archive logs)
LOG_FILE="/tmp/syslog_$HOSTNAME.tar.gz"
tar -czf "$LOG_FILE" /var/log/syslog || {
  echo "{\"error\": \"Log archive failed\"}" && exit 1
}

# Return structured output
cat <<EOF
{
  "message_metadata": {},
  "payload": {
    "result": "success",
    "output_data": {
      "archive": "$LOG_FILE"
    }
  },
  "error": null
}
EOF
```

---

## Required Behavior

- Read structured JSON from stdin
- Return JSON to stdout with keys: `message_metadata`, `payload`, and `error`
- Exit 0 on success, non-zero on error
- Avoid writing logs to stdout—use stderr

---

## Plugin Naming

- Use lowercase kebab-case: `restart-docker.sh`, `noop.sh`
- Filename is treated as the plugin identifier
- File must be executable (`chmod +x plugin.sh`)

---

## Testing Plugins

To test a plugin:

```bash
echo '{
  "payload": {
    "data": {
      "input_parameters": {}
    }
  }
}' | ./restart-docker.sh | jq .
```

Check:

- Valid JSON output
- Correct exit code
- No junk on stdout

---

## Registration

LOM/LMM may eventually auto-register plugins (see MRS). For MVP:

- Plugins are statically mapped in RUNE core
- Place plugins in `plugins/` directory

Future version will support dynamic registration with metadata.

---

## Output Example (Success)

```json
{
  "message_metadata": {},
  "payload": {
    "result": "success",
    "output_data": {
      "archive": "/tmp/syslog_web01.tar.gz"
    }
  },
  "error": null
}
```

## Output Example (Failure)

```json
{
  "message_metadata": {},
  "payload": null,
  "error": {
    "message": "Log archive failed",
    "code": 1001
  }
}
```

---

For plugin execution and message format, see `/docs/protocol_runtime.md` (RCS) and `/docs/protocol_error.md` (EPS).

© 2025 Richard Majewski. Licensed under the MPL-2.0.
