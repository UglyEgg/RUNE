# Mediation model

RUNE enforces a mediation boundary to keep plugin execution safe, consistent, and auditable.

The Local Mediation Module (LMM) is the only component that:

- executes plugins
- selects and configures transports
- interprets plugin output and exit codes
- normalizes failures into EPS

This prevents ad hoc behavior from leaking into the rest of the system.

## Mediation rules

### No direct module to module calls

Modules communicate using RCS messages routed through the LMM. Even when modules run in the same process, the contract is treated as if it were distributed.

### Plugins do not talk to the framework

Plugins communicate only via BPCS stdin and stdout. Plugins do not:

- emit RCS directly
- emit EPS directly
- reach into core state
- decide routing targets

### Registry driven routing

The LMM routes requests using the registry built from MRS data. For plugins, the registry entry includes:

- action name
- plugin path and execution profile
- required parameters and validation hints
- preferred transport (optional)
- timeouts and retry policy (optional)

This allows policy and routing to be centralized.

## Transport selection

The LMM selects transport based on:

- runtime configuration (what transports are enabled)
- node metadata (for example, SSM managed vs SSH only)
- action metadata (for example, action requires local execution)

Transport selection is a mediation concern. LOM and plugins should not contain transport specific logic.

## Output validation and normalization

The LMM treats plugin output as untrusted input. It:

- requires exactly one JSON object on stdout
- validates it against the BPCS expectations
- captures stderr separately as diagnostics
- interprets exit codes and error payloads
- emits EPS for failures that must propagate beyond the plugin boundary

This makes the system predictable for both humans and automation.

## Observability

The LMM propagates identifiers:

- `correlation_id` connects a CLI request to downstream actions
- `trace_id` and `span_id` support distributed tracing style correlation
- `message_id` and `parent_message_id` provide message lineage

These fields exist in the protocols so corporate logging and tracing systems can consume them without bespoke parsing.
