"""SSH transport for executing remote plugins."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from rune.models import TransportResult

DEFAULT_TIMEOUT = 60


def run_remote_plugin_ssh(
    node: str, plugin_path: Path, input_json: dict[str, Any]
) -> TransportResult:
    """Execute the plugin using SSH semantics.

    For the MVP we assume the plugin is available locally and simulate SSH by invoking the
    script directly. The function still captures stdout, stderr, and exit code to match the
    transport contract.
    """

    try:
        completed = subprocess.run(
            ["bash", str(plugin_path)],
            input=json.dumps(input_json),
            text=True,
            capture_output=True,
            timeout=DEFAULT_TIMEOUT,
            check=False,
        )
        return TransportResult(
            stdout=completed.stdout,
            stderr=completed.stderr,
            exit_code=completed.returncode,
        )
    except subprocess.TimeoutExpired as exc:
        return TransportResult(stdout="", stderr=str(exc), exit_code=124)
    except FileNotFoundError as exc:
        return TransportResult(stdout="", stderr=str(exc), exit_code=255)
