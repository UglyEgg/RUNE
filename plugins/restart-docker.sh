#!/usr/bin/env bash
set -euo pipefail

cat <<'JSON'
{
  "message_metadata": {"version": "1.0", "message_id": "restart-docker", "created_at": "1970-01-01T00:00:00Z"},
  "payload": {"result": "success", "output_data": {"message": "docker restarted"}},
  "observability": {"trace_id": "restart-docker", "span_id": "restart-docker"},
  "error": null
}
JSON
