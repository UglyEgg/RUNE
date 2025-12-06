# RUNE Security Model

This document outlines the security principles and safeguards embedded in RUNE's MVP design. The goal is to ensure remote actions are controlled, auditable, and constrained by least privilege.

---

## Threat Model

RUNE is designed to execute remote commands across Linux systems triggered by operators or automated systems. Key risks:

- Unauthorized action execution
- Plugin misuse or privilege escalation
- Leakage of secrets or sensitive output
- Insecure transport of execution payloads

---

## Security Principles

- **Agentless by default**: No long-running daemons on endpoints
- **Transport abstraction**: SSH/SSM handles identity, encryption, and auth
- **Explicit plugin invocation**: No dynamic code injection or reflection
- **Structured I/O**: Prevents script injection or sloppy command output parsing

---

## Authentication

- **SSH**: Leverages host/user SSH keys, sudo restrictions, or bastion models
- **SSM**: IAM-based authentication tied to instance profile or SSO identity

---

## Authorization (MVP Scope)

- CLI can restrict which users can run which plugins
- Plugin whitelist enforced by LOM
- Future: RBAC policy engine tied to user/session metadata

---

## Plugin Execution Boundaries

- Plugins must run as non-root unless explicitly whitelisted
- RUNE can enforce `sudo -u restricted_user` when calling plugins
- Output parsing is validated before being accepted

---

## Secrets Handling

- No secrets should be embedded in plugin code
- Plugins should reference external secret stores (e.g. Vault, SSM Parameter Store)
- Future RUNE version may inject secrets securely via environment or temp file

---

## Audit & Logging

- All invocations should log:

  - Timestamp
  - Target node
  - Action invoked
  - Exit status / trace ID

- Logs written locally and/or sent to centralized observability sink

---

## Hardening Recommendations

- Restrict plugin directory access to root or ops group
- Use SSH key constraints (`from=`, `command=`)
- Use session-level trace ID for every action
- Disable direct shell access to plugin execution host if possible

---

RUNE is not a privilege escalator—it assumes least privilege at every layer. All actions must be deliberate, accountable, and traceable.

© 2025 Richard Majewski. Licensed under the MPL-2.0.
