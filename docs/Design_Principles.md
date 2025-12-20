# Design principles

RUNE is designed for corporate IT operations where safety, auditability, and predictable execution matter more than cleverness.

## Principles

### Protocol first contracts

RUNE uses explicit protocol specifications as the product contract:

- RCS for runtime messages
- MRS for registration and capability discovery
- BPCS for plugin input and output
- EPS for error reporting

This enables stable integration points even as implementation details evolve.

### Mediation as the safety boundary

All execution is mediated by the LMM. Plugins do not:

- choose transports
- call other modules directly
- decide how errors propagate
- invent their own output formats

This concentrates risk control in one place.

### Plugins are capabilities

RUNE is intentionally small. The platform is the runtime and safety boundary. Capabilities live in plugins owned by teams that understand the services they operate.

### Deterministic, machine readable output

RUNE treats free form output as a liability. Plugins emit one JSON object with clear success or error semantics, suitable for:

- automation and policy checks
- searchable logs
- incident timelines

### Observable by default

Every request carries identifiers that support correlation across systems:

- message id and correlation id for request response linkage
- trace id and span id for distributed tracing

### Safe defaults

The LMM enforces guardrails:

- timeouts and retry policy
- output validation
- explicit transport configuration
- explicit plugin paths

### Corporate friendly operational model

RUNE favors patterns that fit common enterprise constraints:

- works with SSH and SSM
- does not require long running agents on targets
- supports controlled plugin distribution and change management
- produces outputs that can be ingested by SIEM and log pipelines

## See also

- [Architecture](architecture.md)
- [Mediation model](mediation_model.md)
