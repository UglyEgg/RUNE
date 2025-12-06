#!/usr/bin/env bash
set -euo pipefail

# Minimal plugin that echoes a fixed success response.
cat <<'JSON'
{
  "message_metadata": {"version": "1.0", "message_id": "noop", "created_at": "1970-01-01T00:00:00Z"},
  "payload": {"result": "success", "output_data": {"message": "noop completed"}},
  "observability": {"trace_id": "noop", "span_id": "noop"},
  "error": null
}
JSON
