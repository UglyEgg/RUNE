# RUNE

RUNE is a remediation execution framework for corporate IT operations. It runs curated recovery actions (plugins) on remote Linux hosts and returns structured, machine readable results.

RUNE is a personal platform project that captures how I think about reliability, mediation, and operational clarity in real-world systems.

RUNE is intentionally not a configuration management system. It does not manage desired state. It executes targeted actions to recover services, validate system health, and automate runbooks with audit friendly output.

## What RUNE is for

- Incident response and service recovery: restart services, fix broken dependencies, validate a repair
- Fleet hygiene checks: run standardized diagnostics and return structured results
- Security and compliance runbooks: verify settings, collect evidence, remediate a narrowly scoped issue
- Operations automation where you need traceable, deterministic execution rather than ad hoc SSH sessions

## What RUNE is not

- Not Ansible, Salt, Puppet, Chef, or a general state enforcement tool
- Not a remote shell wrapper that streams unstructured console output
- Not a patch management system

## How it works

1. An operator or automation trigger requests an action.
2. The Lifecycle Orchestration Module (LOM) validates intent and selects an execution plan.
3. The Local Mediation Module (LMM) routes and executes the action via a transport (SSH or SSM).
4. A plugin runs on the target node and communicates via a strict JSON protocol.
5. Results and errors are returned in stable envelopes suitable for automation, logging, and audit.

RUNE is protocol first. The protocols are the product contract:

- Runtime Communication Specification (RCS): internal runtime messages
- Module Registration Specification (MRS): capability and module registration
- Bash Plugin Communication Specification (BPCS): plugin stdin and stdout contract
- Error Protocol Specification (EPS): standardized errors

## Start here

- [Why RUNE](why_rune.md)
- [Quick Start](quick_start.md)
- [Install](install.md)
- [Architecture](architecture.md)
- [Plugin Developer Guide](plugin_dev_guide.md)
- [Protocols](rcs.md)

## Project status

RUNE is designed as a production grade architecture with a minimal initial implementation. Some features are implemented as profiles or static configuration in early builds, while keeping the same protocol contracts so behavior can scale without breaking integrations.
