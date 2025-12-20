# Testing

RUNE testing has two goals:

- verify the platform behaviors (mediation, transport, normalization)
- verify plugin behaviors (inputs, outputs, exit codes, safety)

In corporate environments, the safest way to scale runbooks is to test them like software.

## Test layers

### 1. Unit tests (core)

Core code should be unit tested for:

- schema validation
- routing decisions based on registry entries
- output normalization and EPS generation
- transport adapter argument formation

### 2. Plugin contract tests

Plugins should be tested for strict BPCS compliance:

- reads one JSON object from stdin
- writes one JSON object to stdout
- returns correct exit code
- never prints structured output to stderr

A simple approach is to keep sample BPCS inputs and expected outputs in a `tests/` directory in the plugin repository.

### 3. Integration tests (local)

Run the CLI against a local container or VM where you control the plugin install path. Validate:

- RCS request construction and correlation
- correct plugin selection and invocation
- output parsing and validation
- error behavior when plugin fails or output is malformed

### 4. Integration tests (staging fleet)

Before enabling a plugin action for production incident use, validate it on:

- representative OS images
- representative service configurations
- representative permission models

## Failure mode testing

A plugin that works only on the happy path is not an operational tool.

Test:

- missing parameters
- dependency failures
- permission failures
- partial success cases
- timeouts

Confirm that failures result in:

- BPCS error payload
- meaningful exit codes
- EPS normalization at the platform boundary

## Operational readiness checks

For each action you intend to run during incidents, capture:

- required privileges
- expected runtime
- safe to rerun guidance
- rollback or compensating actions if needed
- owner team and escalation contact

This information should be stored in the registry metadata (MRS) and the plugin documentation.
