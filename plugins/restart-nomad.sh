#!/usr/bin/env bash
set -euo pipefail

cat <<'JSON'
{
  "message_metadata": {"version": "1.0", "message_id": "restart-nomad", "created_at": "1970-01-01T00:00:00Z"},
  "payload": {"result": "success", "output_data": {"message": "nomad restarted"}},
  "observability": {"trace_id": "restart-nomad", "span_id": "restart-nomad"},
  "error": null
}
JSON
