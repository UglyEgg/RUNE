# Quick Start

This quick start shows an end to end action execution against a remote Linux node.

The goal is to demonstrate the contract:

- CLI triggers an action
- LOM and LMM mediate execution
- plugin receives JSON via stdin (BPCS)
- plugin emits a single JSON object via stdout (BPCS)
- failures are returned as EPS

## Prerequisites

- A Linux host you can reach via SSH (or AWS SSM, if enabled in your build)
- A user with permission to run the required remediation commands
- Python installed locally for the RUNE CLI

## 1. Install the CLI

```bash
python -m pip install rune-framework
```

Verify:

```bash
rune --help
```

## 2. Install a plugin on the target node

RUNE plugins are executables that follow BPCS. The default convention is:

- Plugins: `/opt/rune/plugins/<action>`
- Shared bash library: `/opt/rune/lib/rune_bpcs.sh`

Create a simple health check plugin on the target node:

```bash
sudo install -d /opt/rune/plugins /opt/rune/lib
sudo tee /opt/rune/plugins/health_check >/dev/null <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

# shellcheck disable=SC1091
source /opt/rune/lib/rune_bpcs.sh

# Example: gather a small set of structured facts
UPTIME=$(cut -d. -f1 /proc/uptime)
LOAD=$(cut -d' ' -f1 /proc/loadavg)

rune_ok "Host health collected" "$(jq -n --arg uptime "$UPTIME" --arg load "$LOAD" '{uptime_seconds: ($uptime|tonumber), load_1m: ($load|tonumber)}')"
EOF
sudo chmod +x /opt/rune/plugins/health_check
```

Install the bash library (copy from the repo or release artifact used by your deployment). For development, you can place the project version at `/opt/rune/lib/rune_bpcs.sh`.

## 3. Run the action

```bash
rune run health_check --node myhost01 --json
```

Expected output (shape):

```json
{
  "payload": {
    "result": "success",
    "output_data": {
      "uptime_seconds": 12345,
      "load_1m": 0.12
    }
  },
  "error": null
}
```

## 4. What happens on errors

If a plugin returns a non zero exit code or an `error` payload, the LMM normalizes the failure and returns an EPS error envelope (or an EPS shaped error section in the CLI response, depending on output mode).

In practice, that means:

- your automation can reliably detect failure
- your logging pipeline can index error codes and fingerprints
- operators get a human readable summary that still maps to structured fields

## Next steps

- [Install](install.md) for deployment options and prerequisites
- [Architecture](architecture.md) for component responsibilities and execution flow
- [Plugin Developer Guide](plugin_dev_guide.md) to build real remediation actions
- [BPCS](bpcs.md) for the plugin contract
- [EPS](eps.md) for structured errors
