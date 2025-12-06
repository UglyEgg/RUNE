# RUNE - Remediation & Unified Node Executor

![Docs](https://github.com/UglyEgg/RUNE/actions/workflows/deploy-docs.yml/badge.svg)

RUNE is a modular, extensible orchestration framework designed to standardize and automate common remediation and diagnostic tasks across large Linux-based infrastructures. It enables operators, especially security and platform teams, to quickly execute predefined system actions—such as restarting services, gathering logs, or healing broken components—with a single CLI command or button press from a centralized dashboard.

RUNE acts as a secure, structured execution layer that connects human-initiated actions to system-level operations across fleets of nodes. Actions are written as pluggable scripts (Bash or Python), executed remotely over SSH or SSM, and mediated by a central orchestrator that captures results, handles errors, and ensures consistent output formatting.

---

## MVP Deliverable 🚀

The goal of the MVP is to deliver a fully functional remote action toolkit that meets this core use case:

> **“When a monitoring alert is triggered, a SoC analyst or engineer should be able to click a button or run a simple CLI command to perform healing operations or collect diagnostics from the affected node—safely, securely, and with clear feedback.”**

### ✅ Features Included in MVP

- **Python-based CLI**
  - Run actions via: `rune run <action> --node <host>`
  - Flags for dry-run, output formatting, and SSM mode
- **Orchestrator Module (LOM)**
  - Validates action names
  - Builds structured execution payloads
  - Selects remote transport layer (SSH or SSM)
- **Mediator Module (LMM)**
  - Invokes plugins remotely via transport
  - Sends/receives JSON payloads
  - Parses output and routes responses or errors
- **Remote Execution**
  - Via SSH (default) or AWS SSM (optional)
  - Agentless, no persistent daemons
- **Plugin Architecture**
  - Plugins written in Bash (initially), executed remotely
  - Receive input via JSON stdin, return structured output
- **Core Plugin Set**
  - `gather-logs.sh`
  - `restart-docker.sh`
  - `restart-nomad.sh`
  - `noop.sh` for testing
- **Structured Output & Error Handling**
  - All outputs follow a minimal JSON contract
  - Failures return structured error objects with traceability

---

## Future Potential 🚧

RUNE’s architecture is intentionally modular and forward-thinking. While the MVP is focused and lightweight, the framework is designed to support deeper enterprise-grade functionality with minimal refactoring.

### 🔮 Potential Roadmap Features

- **Plugin Versioning & Capability Discovery**
  - Plugins self-register on load with version metadata
  - CLI introspection via `rune show-available-actions`
- **Persistent Agent Stub (Optional)**
  - Lightweight endpoint service for queued or real-time event reactions
- **Dashboard API Integration**
  - Full REST API for external systems to trigger actions
  - Token-based auth, RBAC, and audit logging
- **Centralized Error Protocol (EPS)**
  - Dedicated module to standardize, escalate, and remediate runtime errors
- **Dynamic Workflow Chaining**
  - Execute multiple actions in sequence: e.g., `gather-logs && restart-service`
- **Plugin Language Expansion**
  - Support Python, Go, or even WASM-based plugins using common contract
- **Observability Enhancements**
  - Send execution traces to external systems (ELK, Splunk, etc.)
  - Correlate actions via trace ID or job ID
- **Secrets and Config Management**
  - Integration with Vault, AWS SSM Parameter Store, etc.

---

## Status

**Project Phase:** MVP in development  
**Language:** Python (Core) + Bash (Plugins)  
**Target Platform:** Linux (agentless, SSH/SSM)  
**License:** MPL-2.0

---

## Contributing

This project is currently under active development. Contributions and plugin ideas are welcome once the core framework is stabilized. Stay tuned.

---

## Contact

Questions? Feature requests?  
Open an issue or [start a discussion](https://github.com/Ugly/rune/discussions) to help shape RUNE’s future.

© 2025 Richard Majewski. Licensed under the MPL-2.0.
