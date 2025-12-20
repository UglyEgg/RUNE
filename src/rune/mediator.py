"""Local Mediation Module implementation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from rune.models import MediatorResult, StructuredError, TransportResult
from rune.transport_ssh import run_remote_plugin_ssh
from rune.transport_ssm import run_remote_plugin_ssm

SUPPORTED_TRANSPORTS = {"ssh", "ssm"}


def _protocol_violation(action: str, node: str, transport: str, message: str) -> MediatorResult:
    error = StructuredError(code=400, message=message)
    return MediatorResult(
        status="failed",
        action=action,
        node=node,
        transport=transport,
        plugin_output=None,
        error=error,
    )


def execute_action(
    action: str,
    node: str,
    plugin_path: Path,
    payload: dict[str, Any],
    transport: str,
) -> MediatorResult:
    """Execute a plugin via the selected transport and normalize its output."""

    if transport not in SUPPORTED_TRANSPORTS:
        return _protocol_violation(action, node, transport, "Unsupported transport")

    if transport == "ssh":
        transport_result = run_remote_plugin_ssh(
            node=node, plugin_path=plugin_path, input_json=payload
        )
    else:
        transport_result = run_remote_plugin_ssm(
            node=node, plugin_path=plugin_path, input_json=payload
        )

    return _normalize_transport_output(
        action=action,
        node=node,
        transport=transport,
        transport_result=transport_result,
    )


def _normalize_transport_output(
    action: str,
    node: str,
    transport: str,
    transport_result: TransportResult,
) -> MediatorResult:
    raw_output = transport_result.stdout.strip()
    if not raw_output:
        return _protocol_violation(action, node, transport, "Empty response from plugin")

    try:
        parsed_output = json.loads(raw_output)
    except json.JSONDecodeError:
        return _protocol_violation(action, node, transport, "Malformed JSON from plugin")

    message_metadata = parsed_output.get("message_metadata")
    observability = parsed_output.get("observability")
    payload = parsed_output.get("payload")
    if (
        not isinstance(message_metadata, dict)
        or not isinstance(observability, dict)
        or not isinstance(payload, dict)
    ):
        return _protocol_violation(action, node, transport, "Missing required BPCS fields")

    result_value = payload.get("result")
    if result_value not in {"success", "error", "dry_run"}:
        return _protocol_violation(action, node, transport, "Invalid payload result field")

    if transport_result.exit_code == 0 and result_value == "success":
        return MediatorResult(
            status="success",
            action=action,
            node=node,
            transport=transport,
            plugin_output=parsed_output,
            error=None,
        )

    plugin_error = parsed_output.get("error")
    structured_error = StructuredError(
        code=int(plugin_error.get("code", transport_result.exit_code or 1))
        if isinstance(plugin_error, dict)
        else int(transport_result.exit_code or 1),
        message=str(plugin_error.get("message", "Plugin signaled failure"))
        if isinstance(plugin_error, dict)
        else "Plugin signaled failure",
        details=plugin_error.get("data") if isinstance(plugin_error, dict) else None,
    )
    return MediatorResult(
        status="failed",
        action=action,
        node=node,
        transport=transport,
        plugin_output=parsed_output,
        error=structured_error,
    )
