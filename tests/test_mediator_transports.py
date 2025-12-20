from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from rune import mediator
from rune.models import TransportResult


def _base_request() -> dict[str, Any]:
    return {
        "message_metadata": {"version": "1.0", "message_id": "1", "created_at": "now"},
        "routing": {"event_type": "noop", "source_module": "test", "target_node": "n1"},
        "observability": {"trace_id": "t", "span_id": "s"},
        "payload": {
            "schema_version": "rcs_v1",
            "content_type": "application/json",
            "data": {"input_parameters": {}},
        },
    }


def test_valid_json_success(monkeypatch, tmp_path: Path):
    def fake_transport(**_: Any) -> TransportResult:
        output = _base_request() | {
            "payload": {"result": "success", "output_data": {"value": 1}},
            "error": None,
        }
        return TransportResult(stdout=json.dumps(output), stderr="", exit_code=0)

    monkeypatch.setattr(mediator, "run_remote_plugin_ssh", fake_transport)
    result = mediator.execute_action(
        action="noop",
        node="n1",
        plugin_path=tmp_path / "noop.sh",
        payload=_base_request(),
        transport="ssh",
    )
    assert result.status == "success"
    assert result.plugin_output["payload"]["output_data"]["value"] == 1


def test_plugin_error(monkeypatch, tmp_path: Path):
    def fake_transport(**_: Any) -> TransportResult:
        output = _base_request() | {
            "payload": {"result": "error", "output_data": {}},
            "error": {"code": 123, "message": "boom"},
        }
        return TransportResult(stdout=json.dumps(output), stderr="", exit_code=1)

    monkeypatch.setattr(mediator, "run_remote_plugin_ssh", fake_transport)
    result = mediator.execute_action(
        action="noop",
        node="n1",
        plugin_path=tmp_path / "noop.sh",
        payload=_base_request(),
        transport="ssh",
    )
    assert result.status == "failed"
    assert result.error is not None
    assert result.error.code == 123


def test_malformed_json(monkeypatch, tmp_path: Path):
    def fake_transport(**_: Any) -> TransportResult:
        return TransportResult(stdout="not-json", stderr="", exit_code=0)

    monkeypatch.setattr(mediator, "run_remote_plugin_ssh", fake_transport)
    result = mediator.execute_action(
        action="noop",
        node="n1",
        plugin_path=tmp_path / "noop.sh",
        payload=_base_request(),
        transport="ssh",
    )
    assert result.status == "failed"
    assert result.error is not None
    assert result.error.code == 400


def test_timeout_handling(monkeypatch, tmp_path: Path):
    def fake_transport(**_: Any) -> TransportResult:
        return TransportResult(stdout="{}", stderr="timeout", exit_code=124)

    monkeypatch.setattr(mediator, "run_remote_plugin_ssh", fake_transport)
    result = mediator.execute_action(
        action="noop",
        node="n1",
        plugin_path=tmp_path / "noop.sh",
        payload=_base_request(),
        transport="ssh",
    )
    assert result.status == "failed"
    assert result.error is not None


def test_bad_transport_selection(tmp_path: Path):
    result = mediator.execute_action(
        action="noop",
        node="n1",
        plugin_path=tmp_path / "noop.sh",
        payload=_base_request(),
        transport="bad",
    )
    assert result.status == "failed"
    assert result.error is not None
    assert result.error.code == 400


def test_missing_bpcs_fields(monkeypatch, tmp_path: Path):
    def fake_transport(**_: Any) -> TransportResult:
        output = json.dumps({"payload": {"result": "success"}})
        return TransportResult(stdout=output, stderr="", exit_code=0)

    monkeypatch.setattr(mediator, "run_remote_plugin_ssh", fake_transport)
    result = mediator.execute_action(
        action="noop",
        node="n1",
        plugin_path=tmp_path / "noop.sh",
        payload=_base_request(),
        transport="ssh",
    )
    assert result.status == "failed"
    assert result.error is not None


def test_invalid_result_value(monkeypatch, tmp_path: Path):
    def fake_transport(**_: Any) -> TransportResult:
        output = json.dumps(
            {
                "message_metadata": _base_request()["message_metadata"],
                "observability": _base_request()["observability"],
                "payload": {"result": "unknown"},
            }
        )
        return TransportResult(stdout=output, stderr="", exit_code=0)

    monkeypatch.setattr(mediator, "run_remote_plugin_ssh", fake_transport)
    result = mediator.execute_action(
        action="noop",
        node="n1",
        plugin_path=tmp_path / "noop.sh",
        payload=_base_request(),
        transport="ssh",
    )
    assert result.status == "failed"
    assert result.error is not None


def test_ssm_transport_path(monkeypatch, tmp_path: Path):
    def fake_transport(**_: Any) -> TransportResult:
        output = _base_request() | {
            "payload": {"result": "success", "output_data": {"via": "ssm"}},
            "error": None,
        }
        return TransportResult(stdout=json.dumps(output), stderr="", exit_code=0)

    monkeypatch.setattr(mediator, "run_remote_plugin_ssm", fake_transport)
    result = mediator.execute_action(
        action="noop",
        node="n1",
        plugin_path=tmp_path / "noop.sh",
        payload=_base_request(),
        transport="ssm",
    )
    assert result.status == "success"
    assert result.plugin_output["payload"]["output_data"]["via"] == "ssm"
