#!/usr/bin/env bash
set -euo pipefail

input_json=$(cat)

if [ -z "$input_json" ]; then
  input_json="{}"
fi

cat <<JSON
{
  "message_metadata": {"version": "1.0", "message_id": "gather-logs", "created_at": "1970-01-01T00:00:00Z"},
  "payload": {
    "result": "success",
    "output_data": {
      "message": "logs gathered",
      "input": $input_json
    }
  },
  "observability": {"trace_id": "gather-logs", "span_id": "gather-logs"},
  "error": null
}
JSON
