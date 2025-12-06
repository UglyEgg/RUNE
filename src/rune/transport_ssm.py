"""SSM transport placeholder for MVP."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from rune.models import TransportResult


def run_remote_plugin_ssm(
    node: str, plugin_path: Path, input_json: dict[str, Any]
) -> TransportResult:
    """Simulate SSM execution of a plugin.

    The MVP implementation validates that AWS configuration exists and otherwise returns
    a structured error encoded as a TransportResult for the mediator to unwrap.
    """

    _ = plugin_path  # plugin path retained for API parity

    if not _has_aws_credentials():
        error_payload = json.dumps(
            {
                "message_metadata": input_json.get("message_metadata", {}),
                "observability": input_json.get("observability", {}),
                "payload": {"result": "error", "output_data": {}},
                "error": {"code": 501, "message": "AWS credentials not configured"},
            }
        )
        return TransportResult(stdout=error_payload, stderr="missing AWS credentials", exit_code=1)

    error_payload = json.dumps(
        {
            "message_metadata": input_json.get("message_metadata", {}),
            "observability": input_json.get("observability", {}),
            "payload": {"result": "error", "output_data": {}},
            "error": {"code": 501, "message": "SSM transport not yet implemented"},
        }
    )
    return TransportResult(stdout=error_payload, stderr="ssm not implemented", exit_code=1)


def _has_aws_credentials() -> bool:
    """Return True if the environment exposes AWS credentials."""

    for key in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN"):
        if key in os.environ:
            return True
    return False
