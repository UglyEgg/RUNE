# Lifecycle model

The Lifecycle Orchestration Module (LOM) is responsible for owning and coordinating the runtime lifecycle of RUNE modules and capabilities.

In early builds, modules may be implemented as in process components. The lifecycle model still applies because it defines responsibilities, not process topology.

## What LOM owns

- action and module registry (built from MRS declarations or static equivalents)
- startup and shutdown ordering for core components
- request validation and execution planning
- policy decisions that should not live in plugins (timeouts, retries, safety flags)
- correlation and trace identifier creation

## Registration and discovery

RUNE uses the Module Registration Specification (MRS) to represent capabilities. In the RUNE profile:

- core modules (LOM, LMM, ErrorHandler) register as modules
- plugins register as capabilities of a plugin module

For deployments that do not want dynamic registration, the same schema can be produced from a static catalog file at startup. This keeps the contract stable while allowing controlled operations.

## Lifecycle states

A module or plugin capability typically moves through:

1. **discovered**: known to the registry
2. **available**: dependencies satisfied and eligible for use
3. **active**: currently in use or running heartbeats
4. **degraded**: reachable but failing health checks
5. **unavailable**: not eligible for routing

These states are used for routing decisions, operator feedback, and error handling.

## Action execution lifecycle

At a high level:

1. CLI request arrives.
2. LOM validates request parameters and selects a registry entry.
3. LOM emits an RCS action execution request to the LMM.
4. LMM executes and returns a result or EPS failure.
5. LOM returns a final response to the CLI.

## Operational controls

In corporate environments, lifecycle is about control:

- a change window can restrict which actions are allowed
- a maintenance mode can disable remediation actions while still allowing diagnostics
- a break glass policy can require explicit operator acknowledgment for high impact actions

These controls belong in LOM policy and registry metadata, not in plugins.
