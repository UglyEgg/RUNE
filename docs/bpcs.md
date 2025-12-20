# Bash Plugin Communication Specification (BPCS)

This is the canonical stdin and stdout contract for RUNE Bash plugins.

The recommended implementation uses the shared Bash library documented in [Bash library reference](bash_library_reference.md).

## Overview

The Bash Plugin Communication Specification (BPCS) defines the standard interface for data exchange between Bash script plugins and the RUNE platform. All plugin communication-input, output, and error handling-is strictly mediated by the RUNE Mediator Module (LMM). No direct communication between plugins and modules, or between plugins, is permitted.

BPCS ensures robust, consistent, and observable integration of Bash plugins, supporting modularity, observability, and system stability.

**Key Principles:**

- **Strict Mediation:** All plugin invocation, input, output, and errors flow through the LMM.
- **No Direct Plugin Communication:** Plugins cannot send messages directly to modules or to one another.
- **Standardized Input/Output:** All plugin messages are structured as JSON.
- **Observability:** All plugin executions are traceable via LMM-managed IDs and logs.
- **Robust Error Handling:** Plugins follow strict exit code and error payload conventions.
- **Security:** Data is sanitized and all communication is managed by the LMM.

## Protocol Architecture Context

BPCS operates as the contract governing all Bash plugin interactions:

| Protocol | Purpose                                           | Managed By                    | Frequency                    |
| -------- | ------------------------------------------------- | ----------------------------- | ---------------------------- |
| **MRS**  | Module/Plugin registration/capability declaration | Orchestrator (LOM)            | Low (startup/shutdown)       |
| **RCS**  | Runtime operational communication                 | Mediator (LMM)                | High (continuous)            |
| **EPS**  | Error handling and recovery messaging             | Mediator (LMM) + ErrorHandler | Variable (exception-based)   |
| **BPCS** | Bash plugin interface definition                  | Mediator (LMM)                | Variable (plugin invocation) |

**Integration Points:**

- **Mediator (LMM):** Sole invoker and mediator for Bash plugins-handles all input, output, and error capture.
- **Orchestrator (LOM):** Handles plugin registration and lifecycle management.
- **Plugins:** Must comply with this specification for all communications.
- **Observability:** All plugin executions are traceable via LMM-managed IDs and logs.

## When to Use This Specification

| Use Case                         | Protocol | Purpose                                       |
| -------------------------------- | -------- | --------------------------------------------- |
| Plugin executes business logic   | **BPCS** | Structured input/output for normal operations |
| Plugin returns data to framework | **BPCS** | Standard result reporting                     |
| Plugin encounters an error       | **BPCS** | Structured error response, supports EPS       |
| Plugin needs traceability        | **BPCS** | Observability metadata (trace_id, span_id)    |
| Operational messaging            | **RCS**  | Core-to-core, non-plugin module communication |
| Module registration              | **MRS**  | Capability declaration                        |
| Error escalation                 | **EPS**  | Framework-level error routing                 |

**Decision Rule:** Use BPCS for all data exchange between Bash plugins and the RUNE framework (input and output). Use EPS for system-level errors outside plugin execution.

## Communication Message Structure

All communication between Bash plugins and the RUNE framework is performed using JSON-encoded messages via standard input (`stdin`) and output (`stdout`). Plugins may also write diagnostic details to standard error (`stderr`).

### Complete Format Example

#### Input Message (from RUNE to Plugin)

```json
{
  "message_metadata": {
    "version": "1.0",
    "message_id": "b4f1c9d4-7f2d-4c5b-90a0-cf5d2c8e3b12",
    "correlation_id": "workflow-abc-123",
    "created_at": "2025-08-03T16:35:00.000Z"
  },
  "payload": {
    "input_parameters": {
      "email_address": "user@example.com",
      "template_id": "welcome-2025"
    },
    "context": {
      "user_id": "user-001",
      "triggered_by": "registration"
    }
  },
  "observability": {
    "trace_id": "trace-abc-001",
    "span_id": "span-bash-plugin-001"
  }
}
```

#### Output Message (from Plugin to RUNE)

```json
{
  "message_metadata": {
    "version": "1.0",
    "message_id": "b4f1c9d4-7f2d-4c5b-90a0-cf5d2c8e3b12",
    "correlation_id": "workflow-abc-123",
    "created_at": "2025-08-03T16:35:01.123Z"
  },
  "payload": {
    "result": "success",
    "output_data": {
      "email_sent": true,
      "delivery_id": "deliv-12345"
    }
  },
  "observability": {
    "trace_id": "trace-abc-001",
    "span_id": "span-bash-plugin-001"
  },
  "error": null
}
```

#### Output Message (Error Case)

```json
{
  "message_metadata": {
    "version": "1.0",
    "message_id": "b4f1c9d4-7f2d-4c5b-90a0-cf5d2c8e3b12",
    "correlation_id": "workflow-abc-123",
    "created_at": "2025-08-03T16:35:01.234Z"
  },
  "payload": null,
  "observability": {
    "trace_id": "trace-abc-001",
    "span_id": "span-bash-plugin-001"
  },
  "error": {
    "code": 1001,
    "message": "Template not found",
    "details": {
      "template_id": "welcome-2025"
    }
  }
}
```

## Field Specifications

### Message Metadata Section

| Field            | Type   | Required | Purpose                               |
| ---------------- | ------ | -------- | ------------------------------------- |
| `version`        | String | **Yes**  | Protocol version (current: "1.0")     |
| `message_id`     | String | **Yes**  | Unique identifier for this message    |
| `correlation_id` | String | No       | Correlates request/response (tracing) |
| `created_at`     | String | **Yes**  | RFC 3339 timestamp, UTC               |

### Payload Section

| Field              | Type   | Required | Purpose                           |
| ------------------ | ------ | -------- | --------------------------------- |
| `input_parameters` | Object | Input    | Named parameters for plugin logic |
| `context`          | Object | Input    | Workflow/user context for plugin  |
| `result`           | String | Output   | `"success"` or `"failure"`        |
| `output_data`      | Object | Output   | Plugin-specific output            |

### Error Section

| Field     | Type    | Required | Purpose                        |
| --------- | ------- | -------- | ------------------------------ |
| `code`    | Integer | Output   | Numeric error code (see below) |
| `message` | String  | Output   | Human-readable error message   |
| `details` | Object  | Output   | Additional error data/context  |

### Observability Section

| Field      | Type   | Required | Purpose                        |
| ---------- | ------ | -------- | ------------------------------ |
| `trace_id` | String | **Yes**  | Distributed tracing identifier |
| `span_id`  | String | **Yes**  | Execution span identifier      |

## Standard Output/Exit Code Conventions

| Plugin Behavior    | stdout            | stderr             | exit code |
| ------------------ | ----------------- | ------------------ | --------- |
| Success            | JSON output       | (optional logs)    | 0         |
| Non-fatal error    | JSON error object | (optional logs)    | 1         |
| Fatal/system error | JSON error object | Error details/logs | >1        |

- **All plugin output must be a single JSON object written to stdout.**
- **stderr** may be used for diagnostics, stack traces, or debug logs (not structured).
- **Exit codes** are mandatory and must be interpreted by the LMM.

## Standard Error Codes and Responses

| Code | Meaning                          | When to Use                         |
| ---- | -------------------------------- | ----------------------------------- |
| 0    | Success                          | Normal operation, result in payload |
| 1    | Plugin validation error          | Input parameter validation failed   |
| 2    | Resource or dependency error     | File, network, or external resource |
| 3    | Business logic failure           | Application logic failed            |
| 4    | Configuration error              | Missing/invalid env or config       |
| 100  | Unhandled exception/system error | Unexpected fatal error              |

> **All error codes >= 1 must include a populated `error` object in the plugin output.**

## Plugin Invocation and Data Flow

1. **Mediator (LMM) prepares input message**
   - Populates all metadata, input parameters, context, and observability fields.
2. **Mediator (LMM) invokes plugin**
   - Plugin receives input as JSON via stdin.
3. **Plugin processes request**
   - Writes structured JSON output to stdout (and optional logs to stderr).
4. **Mediator (LMM) captures stdout/stderr/exit code**
   - Parses stdout as JSON for result or error.
   - Handles exit code according to convention.
5. **Mediator (LMM) routes output**
   - On success, output is routed to consumer(s) via LMM.
   - On error, output is processed per EPS and logged/escalated via LMM.

## Error Handling and Recovery

- Plugins must always return a valid JSON output message, even on error.
- The `error` section must be present and populated if exit code != 0.
- Framework will escalate severe/fatal errors using EPS protocol.
- Plugin errors should include actionable guidance in the `details` field where possible.

## Example Communication Messages

### Success

```json
{
  "message_metadata": {
    "version": "1.0",
    "message_id": "a1b2c3d4-e5f6-7890-1234-56789abcdef0",
    "correlation_id": "workflow-xyz-789",
    "created_at": "2025-08-03T16:36:00.000Z"
  },
  "payload": {
    "result": "success",
    "output_data": {
      "user_created": true,
      "user_id": "user-999"
    }
  },
  "observability": {
    "trace_id": "trace-xyz-002",
    "span_id": "span-plugin-user-creation"
  },
  "error": null
}
```

### Input Validation Error

```json
{
  "message_metadata": {
    "version": "1.0",
    "message_id": "b2c3d4e5-f6a7-8901-2345-6789abcdef01",
    "correlation_id": "workflow-xyz-789",
    "created_at": "2025-08-03T16:36:10.000Z"
  },
  "payload": null,
  "observability": {
    "trace_id": "trace-xyz-002",
    "span_id": "span-plugin-user-creation"
  },
  "error": {
    "code": 1,
    "message": "Missing required parameter: email_address",
    "details": {
      "parameter": "email_address"
    }
  }
}
```

### Fatal Error

```json
{
  "message_metadata": {
    "version": "1.0",
    "message_id": "e5f6a7b8-c9d0-1234-5678-9abcdef01234",
    "correlation_id": "workflow-xyz-789",
    "created_at": "2025-08-03T16:36:20.000Z"
  },
  "payload": null,
  "observability": {
    "trace_id": "trace-xyz-002",
    "span_id": "span-plugin-user-creation"
  },
  "error": {
    "code": 100,
    "message": "Unexpected system failure",
    "details": {
      "exception": "Segmentation fault",
      "hint": "Check plugin dependencies and memory limits"
    }
  }
}
```

## Minimal Required Communication Message

```json
{
  "message_metadata": {
    "version": "1.0",
    "message_id": "minimal-uuid-001",
    "created_at": "2025-08-03T16:37:00.000Z"
  },
  "payload": {
    "result": "success"
  },
  "observability": {
    "trace_id": "minimal-trace-001",
    "span_id": "minimal-span-001"
  }
}
```

## Implementation Guidelines

- **Input Parsing**: Always read stdin as a single JSON object; exit with code 1 and an error message if parsing fails.
- **Output Writing**: Output must be a single line JSON object to stdout; multiline or non-JSON output is not accepted.
- **Error Handling**: Always populate the `error` field on failure, never mix error and output data in the same message.
- **Observability**: Propagate `trace_id` and `span_id` from input to output for full traceability.
- **Exit Codes**: Always use the conventions described above; never exit with 0 on error or with >0 on success.
- **Security**: Never echo sensitive information in payloads or logs; sanitize all outputs.

## Security and Safety Mechanisms

1. **Input Validation**: Reject malformed or unexpected input with a structured error response.
2. **Execution Isolation**: Plugins run in a sandboxed environment managed by the framework.
3. **Sensitive Data Handling**: Do not log secrets or credentials.
4. **Timeouts**: Plugins exceeding allowed execution time are terminated by the framework.
5. **Error Escalation**: Fatal errors are routed to the ErrorHandler via EPS.
6. **Resource Limits**: Controlled via framework (CPU, memory, disk).
7. **Fallback Handling**: On plugin crash without valid output, the framework generates a protocol-compliant fatal error message.

---

This Bash Plugin Communication Specification ensures robust, predictable, and secure integration of Bash plugins within the RUNE platform, supporting modularity, observability, and system stability.
