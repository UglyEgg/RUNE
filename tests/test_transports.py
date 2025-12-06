from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from rune.transport_ssh import run_remote_plugin_ssh
from rune.transport_ssm import run_remote_plugin_ssm


def test_run_remote_plugin_ssh_success(tmp_path: Path):
    plugin = tmp_path / "echo.sh"
    plugin.write_text("#!/usr/bin/env bash\necho '{\"result\":\"ok\"}'\n")
    plugin.chmod(0o755)

    result = run_remote_plugin_ssh("node", plugin, {"payload": {"input_parameters": {}}})
    assert result.exit_code == 0
    assert json.loads(result.stdout)["result"] == "ok"


def test_run_remote_plugin_ssh_timeout(monkeypatch, tmp_path: Path):
    plugin = tmp_path / "timeout.sh"
    plugin.write_text("echo 'noop'")

    def fake_run(*_: object, **__: object):  # pragma: no cover - patched
        raise subprocess.TimeoutExpired(cmd="bash", timeout=60)

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = run_remote_plugin_ssh("node", plugin, {})
    assert result.exit_code == 124
    assert "timed out" in result.stderr


def test_run_remote_plugin_ssh_missing_binary(monkeypatch, tmp_path: Path):
    plugin = tmp_path / "missing.sh"

    def fake_run(*_: object, **__: object):  # pragma: no cover - patched
        raise FileNotFoundError("bash not found")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = run_remote_plugin_ssh("node", plugin, {})
    assert result.exit_code == 255
    assert "bash not found" in result.stderr


def test_run_remote_plugin_ssm_no_credentials(tmp_path: Path, monkeypatch):
    plugin = tmp_path / "noop.sh"
    env = {
        key: os.environ.pop(key, None)
        for key in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN")
    }
    try:
        result = run_remote_plugin_ssm("node", plugin, {})
    finally:
        for key, value in env.items():
            if value is not None:
                os.environ[key] = value
    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["error"]["message"] == "AWS credentials not configured"


def test_run_remote_plugin_ssm_with_credentials(monkeypatch, tmp_path: Path):
    plugin = tmp_path / "noop.sh"
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "abc")
    result = run_remote_plugin_ssm("node", plugin, {"message_metadata": {}, "observability": {}})
    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["error"]["message"] == "SSM transport not yet implemented"
