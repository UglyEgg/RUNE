# Runtime Communication Specification (RCS)

## Overview

The Runtime Communication Specification (RCS) defines the JSON message structure used for all operational messaging within RUNE during plugin and module execution. This protocol enables consistent, observable, and traceable communication between the RUNE core (LMM/LOM) and remote plugin runners.

## Use Cases

- Plugin execution requests and responses
- Status reporting from remote scripts
- Log or data result transmission

## Message Structure

```json
{
  "message_metadata": {
    "version": "1.0",
    "message_id": "<uuid>",
    "created_at": "<rfc3339 UTC timestamp>",
    "correlation_id": "<uuid, optional>"
  },
  "routing": {
    "event_type": "<action_name>",
    "source_module": "<module or CLI identifier>",
    "reply_to": {
      "event_type": "<expected_response_event>",
      "timeout_ms": 3000
    }
  },
  "payload": {
    "schema_version": "rcs_v1",
    "content_type": "application/json",
    "data": {
      "input_parameters": { ... }
    }
  },
  "observability": {
    "trace_id": "<optional-trace-id>"
  }
}
```

## Requirements

- All timestamps must be in RFC 3339 UTC format
- All `message_id` and `correlation_id` values must be UUID v4
- Payload must contain a valid `input_parameters` object for plugins

## Minimal Valid Message

```json
{
  "message_metadata": {
    "version": "1.0",
    "message_id": "...",
    "created_at": "..."
  },
  "routing": {
    "event_type": "gather-logs",
    "source_module": "cli"
  },
  "payload": {
    "schema_version": "rcs_v1",
    "content_type": "application/json",
    "data": {
      "input_parameters": {}
    }
  }
}
```

## Notes

- RCS does not define how plugins are discovered or registered—that is handled via MRS.
- Error conditions must be reported using EPS format, not RCS.
- RCS should remain lightweight to support SSH/SSM transmission.

© 2025 Richard Majewski. Licensed under the MPL-2.0.
