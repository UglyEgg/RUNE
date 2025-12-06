# RUNE API Reference (Planned Interface)

This document outlines the future RUNE REST API for triggering actions, introspecting available plugins, and querying status. It is not required for MVP, but defines the planned structure for dashboard and programmatic integration.

---

## Base URL

```
POST /v1/run
GET  /v1/actions
GET  /v1/status/:job_id
```

---

## Authentication

- Bearer token or mutual TLS (future)
- Headers:

  ```http
  Authorization: Bearer <token>
  Content-Type: application/json
  ```

---

## `POST /v1/run`

Trigger a remote action on a node.

### Request Body

```json
{
  "action": "gather-logs",
  "node": "host-123",
  "parameters": {
    "duration": "5m"
  },
  "trace_id": "optional-guid-here"
}
```

### Response

```json
{
  "job_id": "abc123",
  "status": "submitted",
  "trace_id": "abc123",
  "message": "Action accepted"
}
```

---

## `GET /v1/actions`

List available actions (via MRS metadata).

### Response

```json
[
  {
    "name": "restart-docker",
    "description": "Restarts Docker service",
    "input_schema": {...},
    "output_schema": {...}
  }
]
```

---

## `GET /v1/status/:job_id`

Retrieve execution status and results.

### Response (Success)

```json
{
  "job_id": "abc123",
  "status": "complete",
  "result": {
    "output_data": {
      "archive": "/tmp/logs.tar.gz"
    },
    "exit_code": 0
  }
}
```

### Response (Failure)

```json
{
  "job_id": "abc123",
  "status": "failed",
  "error": {
    "code": -32001,
    "message": "Non-zero exit code",
    "data": {
      "plugin": "restart-nomad",
      "exit_code": 1
    }
  }
}
```

---

## Notes

- Execution is asynchronous
- `job_id` and `trace_id` are UUIDs
- Internally routes through LOM → LMM → plugin → back to client
- Response conforms to RCS or EPS

© 2025 Richard Majewski. Licensed under the MPL-2.0.
