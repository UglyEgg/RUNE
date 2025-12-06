# RUNE Developer Overview

Welcome to the **RUNE Developer Portal**. This section of the documentation is intended for anyone who extends RUNE beyond its core capabilities—whether by writing **plugins**, authoring larger **modules**, or implementing integrations that communicate with RUNE’s internal protocols.

This guide provides a high‑level map of the developer ecosystem and links to deeper resources.

---

## What You Can Build

### **Plugins**

Plugins are executable components—most commonly Bash scripts—that RUNE invokes to perform targeted tasks. Plugins:

- Take structured input via BPCS (Bash Plugin Communication Spec)
- Perform an action on the host
- Return structured output back to RUNE

Typical examples:

- Restarting services
- Collecting logs or health data
- Repairing common issues

Plugins may be:

- **Simple** (a few lines, using `rune_out` / `rune_err` / `rune_finish`)
- **Advanced** (building their own JSON with `jq` and using `rune_ok` / `rune_error`)

---

### **Modules**

Modules bundle multiple plugins and optionally add shared logic, configuration, or state. Modules are appropriate when:

- A feature requires several related actions
- Behavior needs reuse across plugins
- The extension becomes larger than a single script

Modules are the preferred structure for significant RUNE extensions.

---

### **Protocols**

RUNE’s internal communication and plugin interface are defined by several stable protocols:

- **BPCS** — Bash Plugin Communication Specification
- **RCS** — RUNE Communication Schema
- **Envelope Specification** — standardized message format
- **Routing & Observability** — metadata and tracing schema

Understanding these protocols is essential for advanced plugin development and any module that communicates deeply with the RUNE orchestrator.

---

## Developer Documentation Structure

This section of the docs is organized into three major tracks.

### 1. **Plugin Development**

Start here if you want to write scripts that RUNE can execute.

- Beginner plugin tutorial
- Advanced JSON techniques
- Full BPCS library API reference

### 2. **Module Development**

For larger, multi-plugin projects that encapsulate reusable logic.

- Module development guide
- Testing and validation
- Security model and best practices

### 3. **Protocols**

Reference specifications that define how RUNE communicates with plugins and modules.

- BPCS specification
- RCS schema
- Envelope and metadata formats

---

## Who This Section Is For

You should use this section if you are:

- A systems engineer creating automation or repair scripts
- A platform engineer extending RUNE behavior
- A developer implementing deeper integrations with the RUNE runtime
- Anyone who needs to understand how RUNE communicates with external components

If you instead want to _install_ or _operate_ RUNE, visit the **Implementers** section. If you want to work on RUNE’s internal source code, see **Project → Contributing**.

---

## Getting Started

If you are new to RUNE development, begin with:

### 👉 **Plugin Quickstart (Beginner)**

A simple introduction to writing plugins using the new accumulator API.

If you already know Bash and want full control over JSON:

### 👉 **Advanced Plugin JSON Guide**

Teaches how to construct precise JSON output using `jq` and the low-level APIs.

For large-scale extensions:

### 👉 **Module Development Guide**

Explains structuring, packaging, and testing modules.

---

## Need Help?

If you want additional examples, architecture diagrams, or deeper explanations, reach out or check the **RUNE Implementation Guide** for broader conceptual context.

Welcome to the RUNE developer ecosystem—build boldly!
