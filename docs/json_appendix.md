# JSON appendix

This appendix provides example messages for common RUNE flows.

These are examples. They illustrate shape and intent. Field sets can be extended as needed, but the envelope sections should remain stable.

## 1. Plugin registration (MRS)

```json
{
  "module_identity": {
    "module_name": "PluginBundle_CoreOps",
    "module_class": "PluginProvider",
    "module_type": "plugin_provider",
    "module_version": "1.0.0",
    "description": "Core operations plugin bundle",
    "registration_timestamp": "2025-12-18T00:00:00Z"
  },
  "capability_declaration": {
    "provides_events": [
      {
        "event_type": "ACTION.health_check",
        "description": "Collect basic host health facts",
        "schema_version": "1.0",
        "backward_compatible": true
      }
    ]
  },
  "service_metadata": {
    "owner_team": "Platform Operations",
    "routing_hints": {
      "plugin_path": "/opt/rune/plugins/health_check",
      "default_transport": "ssh",
      "timeout_ms": 60000
    }
  }
}
```

## 2. Action execute request (RCS)

```json
{
  "message_metadata": {
    "version": "1.0",
    "message_id": "msg-001",
    "correlation_id": "req-123",
    "created_at": "2025-12-18T00:00:00Z"
  },
  "routing": {
    "event_type": "ACTION_EXECUTE_REQUEST",
    "event_category": "orchestration",
    "source_module": "CLI",
    "target_module": "LMM",
    "routing_tags": ["action:health_check"],
    "timeout_ms": 60000
  },
  "payload": {
    "schema_version": "bpcs_v1",
    "content_type": "application/json",
    "encoding": "utf-8",
    "data": {
      "input_parameters": {},
      "context": { "node": "myhost01", "triggered_by": "cli" }
    }
  },
  "observability": {
    "trace_id": "trace-abc-001",
    "span_id": "span-cli-001"
  }
}
```

## 3. Plugin input (BPCS stdin)

```json
{
  "message_metadata": {
    "version": "1.0",
    "message_id": "bpcs-001",
    "correlation_id": "req-123",
    "created_at": "2025-12-18T00:00:01Z"
  },
  "payload": {
    "input_parameters": {},
    "context": { "node": "myhost01", "triggered_by": "cli" }
  },
  "observability": {
    "trace_id": "trace-abc-001",
    "span_id": "span-plugin-001"
  }
}
```

## 4. Plugin success output (BPCS stdout)

```json
{
  "message_metadata": {
    "version": "1.0",
    "message_id": "bpcs-001",
    "correlation_id": "req-123",
    "created_at": "2025-12-18T00:00:02Z"
  },
  "payload": {
    "result": "success",
    "output_data": { "uptime_seconds": 12345, "load_1m": 0.12 }
  },
  "observability": {
    "trace_id": "trace-abc-001",
    "span_id": "span-plugin-001"
  },
  "error": null
}
```

## 5. Plugin failure output (BPCS stdout)

```json
{
  "message_metadata": {
    "version": "1.0",
    "message_id": "bpcs-001",
    "correlation_id": "req-123",
    "created_at": "2025-12-18T00:00:02Z"
  },
  "payload": null,
  "observability": {
    "trace_id": "trace-abc-001",
    "span_id": "span-plugin-001"
  },
  "error": {
    "code": 2,
    "message": "Dependency missing",
    "details": { "binary": "systemctl" }
  }
}
```

## 6. Platform normalized error (EPS)

```json
{
  "message_metadata": {
    "version": "1.0",
    "message_id": "eps-001",
    "correlation_id": "req-123",
    "created_at": "2025-12-18T00:00:02Z",
    "priority": "high"
  },
  "routing": {
    "event_type": "EPS_ERROR_RESPONSE",
    "event_category": "error_handling",
    "source_module": "LMM",
    "target_module": "ErrorHandler_Core",
    "routing_tags": ["plugin_failure"]
  },
  "error_payload": {
    "error_data": {
      "error_code": 32010,
      "error_type": "PLUGIN_FAILURE",
      "error_message": "Plugin reported an error",
      "severity": "error",
      "recoverable": true,
      "details": {
        "plugin_error_code": 2,
        "plugin_error_message": "Dependency missing",
        "node": "myhost01",
        "action": "health_check"
      }
    },
    "error_context": {
      "origin_module": "LMM",
      "timestamp": "2025-12-18T00:00:02Z",
      "recovery_actions": [
        "Install missing dependency on the node",
        "Verify plugin prerequisites and packaging"
      ],
      "system_impact": "single_request"
    }
  },
  "observability": {
    "trace_id": "trace-abc-001",
    "span_id": "span-lmm-001",
    "error_fingerprint": "plugin_dependency_missing_001"
  }
}
```
