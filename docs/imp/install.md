# Installation Guide

This document explains how to install, configure, and validate **RUNE** on a control node. RUNE is agentless—remote hosts require no installation.

---

## 1. Requirements

### Control Node

- Linux system (recommended)
- Python **3.10+**
- Ability to reach remote hosts via SSH or AWS SSM
- `pip` or another Python package manager

### Remote Hosts

- Linux
- `/bin/bash`
- SSH access **or** SSM connectivity
- Standard system utilities (depending on plugins)

No Python, no RUNE package, no agents required on remote machines.

---

## 2. Install the RUNE CLI

```bash
pip install rune-cli
```

Check installation:

```bash
rune --version
```

If this fails, verify that your `PATH` includes your Python `bin` directory.

---

## 3. Verify Python Environment

RUNE supports Python 3.10 and newer.

Check your version:

```bash
python3 --version
```

If you need to pin a specific interpreter, create a virtual environment:

```bash
python3 -m venv ~/.venv/rune
source ~/.venv/rune/bin/activate
pip install rune-cli
```

---

## 4. Initial Configuration

RUNE uses XDG-style configuration paths.

Create your config directory:

```bash
mkdir -p ~/.config/rune
```

Add a configuration file:

```bash
nano ~/.config/rune/config.toml
```

Minimal SSH-based example:

```toml
[core]
default_transport = "ssh"
default_user = "admin"

[ssh]
private_key = "/home/admin/.ssh/id_ed25519"
known_hosts = "/home/admin/.ssh/known_hosts"
```

Optional SSM configuration:

```toml
[ssm]
region = "us-east-1"
iam_role = "arn:aws:iam::<account-id>:role/YourSSMRole"
```

---

## 5. Test Connectivity

Ensure SSH access works:

```bash
ssh admin@web01
```

If using SSM, test permission boundaries via AWS CLI:

```bash
aws ssm describe-instance-information
```

---

## 6. Validate RUNE Operation

Test a built-in plugin:

```bash
rune run noop --node web01 --output pretty
```

You should receive structured JSON indicating success.

For remote failures, RUNE returns strict EPS-formatted errors so you can debug quickly.

---

## 7. Directory Structure Overview

After installation, RUNE lives in your Python environment:

```
rune/
  cli.py
  core/
  transports/
  plugins/builtin/
  models/
  config/
```

User-level plugins can be stored here:

```
~/.local/share/rune/plugins/
```

System-wide plugins here:

```
/opt/rune/plugins/
```

---

## 8. Upgrading RUNE

```bash
pip install --upgrade rune-cli
```

RUNE maintains compatibility across patch versions for all public protocols (RCS, EPS, BPCS).

---

## 9. Next Steps

- [Quick Start](quick_start.md)
- [Plugin Development Guide](../dev/plugins/beginner_plugin.md)
- [RUNE Implementation Guide](../imp/rune_implementation_guide.md)
- [System Architecture](../contrib/architecture.md)

RUNE is built to be small, predictable, and safe—everything you need for fast operational response.

© 2025 Richard Majewski. Licensed under the MPL-2.0.
