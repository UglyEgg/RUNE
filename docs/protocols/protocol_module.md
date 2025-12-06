# Module Registration Specification (MRS)

> **Status:** Defined and reserved for post-MVP use.  
> The MVP does not yet perform dynamic module registration, but all future
> capability discovery (e.g., S3 log sinks, Vault integration, external
> remediation providers) will conform to this specification.

## Purpose

Defines the registration format and process for RUNE modules and plugins. Modules declare their capabilities, supported actions, metadata, and schema versions through this protocol. This specification ensures that the RUNE Orchestrator (LOM) can discover and validate the available actions at runtime.

## Scope

This protocol is invoked during startup, registration time, or when explicitly requested by the LOM. All modules and plugins must comply with this schema to be discoverable.

## Registration Payload

```json
{
  "registration_metadata": {
    "module_name": "restart-nomad",
    "module_version": "1.0.0",
    "registered_at": "2025-12-01T00:00:00Z"
  },
  "capabilities": [
    {
      "action": "restart-nomad",
      "description": "Restarts Nomad systemd unit",
      "input_schema": {
        "type": "object",
        "properties": {},
        "required": []
      },
      "output_schema": {
        "type": "object",
        "properties": {
          "result": { "type": "string" }
        },
        "required": ["result"]
      }
    }
  ]
}
```

## Key Fields

- `module_name`: Unique, lowercase identifier of the plugin or module
- `module_version`: Semantic version of the module or plugin
- `registered_at`: RFC 3339 timestamp (UTC)
- `capabilities[]`: List of actions this module supports

  - `input_schema`: JSON Schema object describing expected inputs
  - `output_schema`: JSON Schema object describing the structure of valid output

## Requirements

- Each module must register exactly once per runtime session
- Duplicate names will be rejected
- Version resolution will favor latest for conflicting module names

## Notes

- MRS is invoked by LOM directly, not over the runtime channel
- Capability schemas may be stored for CLI introspection or dashboard use

© 2025 Richard Majewski. Licensed under the MPL-2.0.
