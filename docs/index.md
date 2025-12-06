# Welcome to RUNE

**RUNE (Remediation & Unified Node Executor)** is a modular orchestration tool built for Linux environments. It lets security and platform teams quickly respond to system alerts by triggering automated actions—like gathering logs or restarting services—across remote systems via CLI or dashboard.

---

## What is RUNE?

RUNE is designed to:

- Execute predefined remote actions safely and consistently
- Return structured, machine-readable results
- Be agentless by default, using SSH or SSM
- Support plugins written in Bash or Python

---

## Key Concepts

- **Actions**: Discrete operations like `restart-docker` or `gather-logs`
- **Plugins**: Scripts that implement those actions, conforming to a communication spec
- **LOM/LMM**: Python core modules that coordinate execution and capture results

---

## Getting Started

Explore these key documents:

- [Plugin Development Guide](plugin_development_guide.md)
- [System Architecture](system_architecture.md)
- [Runtime Communication Spec (RCS)](protocol_runtime.md)
- [API Reference](api_reference.md)

Want to help? [Contribute](contrib/contributing.md) or follow the [Roadmap](roadmap.md) to see what's next.

---

## Why RUNE?

Because clicking a button should be all it takes to recover a system.

**_Simple to run. Safe to trust. Built to grow._**

© 2025 Richard Majewski. Licensed under the MPL-2.0.
