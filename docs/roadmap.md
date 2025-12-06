# RUNE Development Roadmap

This document outlines the staged development plan for RUNE, with the goal of balancing rapid MVP delivery against long-term architectural flexibility. Each phase builds on the last, expanding RUNE's capabilities without introducing bloat or unnecessary complexity.

---

## 🚀 Phase 1: MVP Delivery (Current Focus)

> Core goal: Execute healing and diagnostic operations on Linux nodes via CLI and/or dashboard API trigger, using remote plugin invocation over SSH or SSM.

### 🔧 Deliverables

- [x] `rune_cli.py`: Command-line interface with `run` subcommand
- [x] `orchestrator.py`: Action validation, plugin resolution
- [x] `mediator.py`: Remote plugin runner, I/O router
- [x] `transport_ssh.py`: Execute plugin via SSH
- [ ] `transport_ssm.py`: Execute plugin via AWS SSM (optional fallback)
- [x] Bash plugins:
  - `gather-logs.sh`
  - `restart-docker.sh`
  - `restart-nomad.sh`
  - `noop.sh`
- [x] Bash Plugin Communication Spec (BPCS v0.1)
- [x] Structured stdout/stderr/output with JSON validation
- [x] CLI flags: `--dry-run`, `--output json|pretty`, `--use-ssm`
- [x] Logging & output capture to local logs or stdout

---

## 🧱 Phase 2: Framework Hardening

> Add developer-quality tooling, formal interfaces, and observability layers to stabilize RUNE as a platform.

### 🧪 Testing & Dev Tooling

- [ ] Unit test coverage for LOM and LMM
- [ ] Integration test harness (mock transport layer)
- [ ] Plugin test framework (stdin → plugin → JSON validator)
- [ ] Basic telemetry for plugin runtime, failure rate, duration

### ⚙️ Plugin Runtime Improvements

- [ ] Versioned plugin discovery
- [ ] Registry of known plugins with metadata (name, description, version, tags)
- [ ] Environment validation prior to plugin exec (e.g., `systemd` available?)

### 🔐 Security / Access Control

- [ ] Execution audit trail (host, user, action, timestamp)
- [ ] Optional sudo enforcement or policy filtering
- [ ] CLI session token or execution fingerprint

---

## 🌐 Phase 3: Remote API + GUI Integration

> Enable RUNE to be triggered from external dashboards, alerting systems, or automation platforms.

### 📡 API & Dashboard Integration

- [ ] REST API to trigger actions (`POST /run/<action>`)
- [ ] AuthN/AuthZ layer (token-based or OIDC)
- [ ] Integration with SoC GUI to trigger RUNE via button
- [ ] Response output routing to dashboard (WebSocket or polling)

---

## 🧠 Phase 4: Workflow & Orchestration Expansion

> Allow RUNE to execute multi-step workflows, aggregate outputs, and implement conditional or sequential logic.

### 🔄 Workflow Engine (Lightweight)

- [ ] Sequential action chaining
- [ ] Conditional branching (`if restart failed, gather-logs`)
- [ ] Parallel execution (across nodes)
- [ ] Reusable workflow definitions in YAML/JSON

---

## 🔮 Phase 5: Enterprise Features & Ecosystem

> Solidify RUNE as a powerful, extensible automation fabric for large-scale Linux infrastructure.

### 🔐 Security & Policy

- [ ] Role-based policy to restrict plugins/actions per operator
- [ ] Secrets integration (Vault, AWS SSM Parameter Store)

### 🌍 Ecosystem & Distribution

- [ ] Plugin packaging and versioning
- [ ] CLI introspection: `rune list-actions`, `rune plugin-info`
- [ ] Community plugin registry or sharing system

### 📊 Observability & Reporting

- [ ] Send trace data to ELK/Splunk
- [ ] Correlation IDs and distributed trace support
- [ ] Execution metrics dashboard (Grafana/Prometheus-friendly)

---

## 🧭 Roadmap Philosophy

- Build fast. Stay lean.
- Prioritize simplicity, modularity, and explicit behavior.
- Agentless first, agents only if necessary.
- Always return structured output—RUNE should be machine- and human-readable.

---

_This roadmap is a living document. Pull requests welcome for additions, edits, or discussion._

© 2025 Richard Majewski. Licensed under the MPL-2.0.
