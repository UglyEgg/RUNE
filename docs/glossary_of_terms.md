# RUNE Glossary of Terms

A reference for acronyms, modules, and naming conventions used throughout the RUNE framework.

---

### RUNE

**Remediation & Unified Node Executor** — The name of the framework. Modular, CLI-driven orchestration engine for Linux environments.

---

### LOM

**Lifecycle Orchestration Module** — Handles incoming execution requests, validates inputs, selects the correct plugin, and delegates to the LMM.

---

### LMM

**Local Mediation Module** — Executes plugins remotely over SSH or SSM, captures output, enforces structured communication, and returns results.

---

### RCS

**Runtime Communication Specification** — The protocol that defines how action execution messages are structured and routed.

---

### EPS

**Error Protocol Specification** — Defines how errors are captured, formatted, and routed inside the RUNE system.

---

### MRS

**Module Registration Specification** — Used to declare plugin/module capabilities (name, schema, version) for introspection and validation.

---

### Plugin

A standalone Bash or Python script that conforms to the RUNE protocol and performs a specific system-level operation.

---

### BPCS

**Bash Plugin Communication Specification** — Contract that all Bash-based plugins must follow. Input via stdin, output via stdout in JSON.

---

### CLI

Command Line Interface — The `rune` terminal command used to run actions like `rune run restart-docker --node web01`

---

### SSM

**AWS Systems Manager** — Optional agent-based transport method for executing remote commands without SSH.

---

### Trace ID / Span ID

Unique identifiers used to track actions across distributed components and log trails.

---

### Job ID

A unique identifier representing one execution instance of a plugin.

---

### Action

The logical name of an operation that RUNE can execute, such as `gather-logs`, `restart-docker`, or `noop`.

---

### Plugin Directory

Location where registered plugins reside. Example: `plugins/` folder under project root.

---

### Payload

The body of a structured JSON message that includes the data to be passed into or out of an action execution.

---

### exit code

Integer returned by a plugin indicating success (`0`) or failure (`1+`). Must be consistent with structured output.

---

This glossary will evolve as RUNE expands. PRs welcome for new terms.

© 2025 Richard Majewski. Licensed under the MPL-2.0.
