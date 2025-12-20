# Plugin developer guide

RUNE plugins are the primary way to extend the platform. A plugin is an executable on the target node that performs a narrow operational task and returns a structured result.

This guide is written for corporate IT and SRE teams building real remediation actions.

## Requirements

A plugin must:

- read one JSON object from stdin (BPCS input)
- write exactly one JSON object to stdout (BPCS output)
- exit with a meaningful code as defined by BPCS
- avoid writing structured data to stderr

Plugins should:

- be idempotent when feasible
- validate inputs early and fail fast
- keep scope narrow and explicit
- avoid printing secrets

## Recommended filesystem layout

- Plugin: `/opt/rune/plugins/<action_name>`
- Shared bash library: `/opt/rune/lib/rune_bpcs.sh`

Standard paths reduce operational friction, packaging work, and incident confusion.

## Bash plugin template

```bash
#!/usr/bin/env bash
set -euo pipefail

# shellcheck disable=SC1091
source /opt/rune/lib/rune_bpcs.sh

# Read input parameters
SERVICE=$(rune_param "service" "")
if [[ -z "$SERVICE" ]]; then
  rune_fail 1 "Missing required parameter: service" '{"parameter":"service"}'
fi

# Example action
systemctl restart "$SERVICE"

# Return structured output
rune_ok "Service restarted" "$(jq -n --arg service "$SERVICE" '{service:$service, restarted:true}')"
```

See [Bash library reference](bash_library_reference.md) for the helper functions.

## Input validation

Validation errors should:

- return a non zero exit code
- populate the `error` object in stdout JSON
- include a stable numeric code and a concise message

Avoid dumping unstructured text into stdout. Keep stdout reserved for the BPCS JSON object.

## Operational safety

### Least privilege

Use a dedicated OS account where possible and grant only required sudo rights for the actions you ship.

### Idempotency and reversibility

If an action is not idempotent, document it in the action registry metadata and consider requiring explicit operator confirmation.

### Timeouts

Plugins should not run forever. The LMM will enforce timeouts, but plugins should also use reasonable internal timeouts for external commands.

## Testing plugins

- test locally with a captured BPCS input JSON file
- test on a staging node that matches production images
- simulate failure modes and confirm BPCS and EPS behaviors

See [Testing](testing.md) for patterns.

## Documenting a plugin

For each plugin, document:

- purpose
- required parameters
- expected output fields
- required privileges
- safe to rerun guidance
- known failure modes

This documentation is as important as the code in corporate environments.
