from __future__ import annotations

import json
from typing import Any

import rune.rune_cli as rune_cli
from rune import orchestrator
from rune.mediator import MediatorResult
from rune.models import StructuredError, build_message_metadata, build_observability
from rune.rune_cli import main


def _success_output() -> dict[str, Any]:
    return {
        "message_metadata": build_message_metadata(),
        "observability": build_observability(),
        "payload": {"result": "success", "output_data": {"echo": True}},
        "error": None,
    }


def test_list_actions_contains_expected_entries():
    actions = orchestrator.list_actions()
    names = {action.name for action in actions}
    assert {"noop", "gather-logs", "restart-docker", "restart-nomad"}.issubset(names)


def test_run_action_dry_run_returns_payload():
    result = orchestrator.run_action(
        action="noop",
        node="test-node",
        use_ssm=False,
        dry_run=True,
        params={"key": "value"},
    )
    assert result.status == "dry_run"
    assert result.plugin_output is not None
    assert result.plugin_output["payload"]["output_data"]["input_parameters"] == {"key": "value"}


def test_run_action_unknown_action_reports_error():
    result = orchestrator.run_action(
        action="unknown",
        node="node1",
        use_ssm=False,
        dry_run=False,
        params={},
    )
    assert result.status == "failed"
    assert result.error is not None
    assert result.error.code == 404


def test_run_action_success_path(monkeypatch):
    def fake_execute_action(**_: Any) -> MediatorResult:
        return MediatorResult(
            status="success",
            action="noop",
            node="node1",
            transport="ssh",
            plugin_output=_success_output(),
            error=None,
        )

    monkeypatch.setattr(orchestrator, "execute_action", fake_execute_action)
    result = orchestrator.run_action(
        action="noop",
        node="node1",
        use_ssm=False,
        dry_run=False,
        params={},
    )
    assert result.status == "success"
    assert result.plugin_output["payload"]["output_data"]["echo"]


def test_run_action_failure_propagates(monkeypatch):
    def fake_execute_action(**_: Any) -> MediatorResult:
        return MediatorResult(
            status="failed",
            action="noop",
            node="node1",
            transport="ssh",
            plugin_output=_success_output(),
            error=StructuredError(code=500, message="boom"),
        )

    monkeypatch.setattr(orchestrator, "execute_action", fake_execute_action)
    result = orchestrator.run_action(
        action="noop",
        node="node1",
        use_ssm=False,
        dry_run=False,
        params={},
    )
    assert result.status == "failed"
    assert result.error is not None
    assert result.error.code == 500


def test_cli_run_integration(monkeypatch, capsys):
    def fake_run_action(**_: Any):
        return orchestrator.OrchestrationResult(
            status="success",
            action="noop",
            node="fakehost",
            transport="ssh",
            message_metadata=build_message_metadata(),
            observability=build_observability(),
            plugin_output=_success_output(),
            error=None,
        )

    monkeypatch.setattr(rune_cli, "run_action", fake_run_action)
    exit_code = main(["run", "noop", "--node", "fakehost", "--output", "json"])
    captured = capsys.readouterr().out
    assert exit_code == 0
    data = json.loads(captured)
    assert data["status"] == "success"
    assert data["plugin_output"]["payload"]["result"] == "success"


def test_cli_list_actions_pretty_output(capsys):
    exit_code = main(["list-actions", "--output", "pretty"])
    assert exit_code == 0
    captured = capsys.readouterr().out
    parsed = json.loads(captured)
    assert "actions" in parsed
    assert any(action["name"] == "noop" for action in parsed["actions"])


def test_cli_param_parse_error(capsys):
    exit_code = main(["run", "noop", "--node", "n1", "--param", "badparam"])
    assert exit_code == 2
    out = capsys.readouterr()
    assert "error" in out.err


def test_cli_failure_exit_code(monkeypatch, capsys):
    def fake_run_action(**_: Any):
        return orchestrator.OrchestrationResult(
            status="failed",
            action="noop",
            node="n1",
            transport="ssh",
            message_metadata=build_message_metadata(),
            observability=build_observability(),
            plugin_output=None,
            error=StructuredError(code=500, message="boom"),
        )

    monkeypatch.setattr(rune_cli, "run_action", fake_run_action)
    exit_code = main(["run", "noop", "--node", "n1"])
    captured = capsys.readouterr().out
    assert exit_code == 1
    data = json.loads(captured)
    assert data["status"] == "failed"
