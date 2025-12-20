# API reference

This document describes the operator facing CLI surface and the protocol level contracts that make RUNE automation friendly.

If you are looking for message formats, start with [RCS](rcs.md), [BPCS](bpcs.md), and [EPS](eps.md).

## CLI surface

### Execute an action

```bash
rune run <action> --node <hostname-or-node-id> [--param key=value ...] [--json]
```

- `action`: registry name of the action to run
- `--node`: target node identifier
- `--param key=value`: repeatable key value parameters passed to the plugin input
- `--json`: emit machine readable output

### Output shape

In JSON mode, the CLI emits a stable success or failure shape:

- Success: BPCS style payload with `error: null`
- Failure: an EPS envelope (or an EPS shaped error object) depending on output mode

The intent is that automation can reliably detect failures without parsing console text.

### Exit codes

The CLI should follow standard conventions:

- `0` success
- non zero failure

Plugins may use more granular exit codes. The LMM interprets them using BPCS conventions.

## Python API surface (library mode)

RUNE is designed so core components can be embedded in automation:

- LOM validates requests and consults registry
- LMM executes via transport and normalizes results

Public Python APIs are intentionally small. The stable contracts are the protocols.

## Protocol level API

The most stable interfaces in RUNE are message contracts.

- Runtime requests and responses use RCS envelopes.
- Capability registration uses MRS.
- Plugins use BPCS on stdin and stdout.
- Errors that must propagate are expressed as EPS.

This makes the system suitable for integration with:

- ticketing workflows
- SOAR tooling
- chatops bots
- CI pipelines
- internal runbook automation
