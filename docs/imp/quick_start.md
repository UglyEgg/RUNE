# Quick Start

This guide walks you through using **RUNE** within minutes. RUNE requires:

- A Linux control node with Python 3.10+
- SSH access to your remote hosts (SSM optional)
- No agents or additional software on remote nodes

---

## 1. Install RUNE

```bash
pip install rune-cli
```

Verify installation:

```bash
rune --help
```

---

## 2. Configure SSH Access

RUNE defaults to SSH. Ensure you can connect:

```bash
ssh admin@web01
```

Create a config file:

```bash
mkdir -p ~/.config/rune
nano ~/.config/rune/config.toml
```

Example:

```toml
[core]
default_transport = "ssh"
default_user = "admin"

[ssh]
private_key = "/home/admin/.ssh/id_ed25519"
known_hosts = "/home/admin/.ssh/known_hosts"
```

---

## 3. Test with the Built‑In `noop` Plugin

```bash
rune run noop --node web01 --output pretty
```

This validates:

- SSH connectivity
- Plugin shipping & execution
- Mediator parsing & structured output

Expected output:

```json
{
  "payload": {
    "result": "success",
    "output_data": {
      "message": "noop completed"
    }
  },
  "error": null
}
```

---

## 4. Run Real Actions

Gather logs:

```bash
rune run gather-logs --node web01
```

Restart Docker:

```bash
rune run restart-docker --node web02
```

Restart Nomad services:

```bash
rune run restart-nomad --node job-runner-1
```

All actions:

- Ship a plugin to the remote node
- Execute it
- Capture structured JSON output
- Clean up (unless configured otherwise)

---

## 5. Optional: Use AWS SSM

Enable SSM transport in your config:

```toml
[core]
default_transport = "ssm"

[ssm]
region = "us-east-1"
iam_role = "arn:aws:iam::<account-id>:role/YourSSMRole"
```

Execute via SSM:

```bash
rune run gather-logs --node i-0123456789abcdef --use-ssm
```

---

## 6. Write Your First Plugin

Example plugin:

```bash
#!/bin/bash
set -euo pipefail
INPUT=$(cat)
cat <<EOF
{
  "payload": {
    "result": "success",
    "output_data": {
      "time": "$(date)"
    }
  },
  "error": null
}
EOF
```

Save to:

```
~/.local/share/rune/plugins/
```

Run:

```bash
rune run myplugin --node web01
```

---

## 7. Next Steps

- [Why RUNE?](../why_rune.md)
- [System Architecture](../contrib/architecture.md)
- [Plugin Development Guide](../dev/plugins/beginner_plugin.md)
- [RUNE Implementation Guide](rune_implementation_guide.md)

RUNE is easy to start, powerful to extend.

© 2025 Richard Majewski. Licensed under the MPL-2.0.
