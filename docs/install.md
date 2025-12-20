# Install

This page describes how to install and deploy RUNE in a corporate IT environment.

RUNE has two installation surfaces:

- Local operator surface: the CLI and core modules (LOM and LMM)
- Remote execution surface: a plugin bundle on the target node

## Local requirements

- Python 3.12 or newer (3.13 supported)
- Network access to target nodes (SSH) or to AWS APIs (SSM), depending on transport
- A way to provide credentials to the selected transport (SSH keys, SSM instance profile)

## Install the CLI (developer and lightweight deployments)

```bash
python -m pip install rune-framework
```

If you are using virtual environments:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install rune-framework
```

## Remote node requirements

RUNE does not require a daemon on the target node. It executes plugins using the selected transport.

Typical requirements for Bash plugins:

- `/bin/bash`
- `jq` (recommended for building JSON safely)
- permissions to perform the remediation actions

### Default filesystem conventions

These paths are conventions used by the reference implementation:

- Plugins: `/opt/rune/plugins/`
- Shared bash library: `/opt/rune/lib/rune_bpcs.sh`
- Optional logs: `/var/log/rune/` (only if you choose to persist local plugin logs)

You can change these via configuration, but standardizing paths helps operations and packaging.

## Plugin bundle distribution

In most environments, you will want a controlled way to ship plugins:

- internal package repository (RPM/DEB)
- golden image or AMI bake
- configuration management for file distribution only
- artifact sync from object storage

RUNE itself does not mandate how you distribute plugins. It only requires that the plugin executable and any required shared libraries are present on the node.

## Enterprise packaging

A common enterprise approach is:

- distribute the CLI as a Python package to operator workstations or automation runners
- distribute plugins as OS packages (RPM/DEB) owned by an internal team

The protocol contracts allow this split without changing the runtime behavior.

## Configuration

RUNE configuration is designed for predictable operations:

- explicit transport configuration
- explicit plugin path configuration
- explicit timeouts and safety limits

See [Architecture](architecture.md) for where configuration is applied, and [Mediation Model](mediation_model.md) for the control points the LMM enforces.
