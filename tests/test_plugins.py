from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from rune.models import build_message_metadata, build_observability

PLUGINS = [
    "gather-logs.sh",
    "restart-docker.sh",
    "restart-nomad.sh",
    "noop.sh",
]


def _base_input(params: dict) -> str:
    data = {
        "message_metadata": build_message_metadata(),
        "routing": {"event_type": "noop", "source_module": "test", "target_node": "local"},
        "observability": build_observability(),
        "payload": {
            "schema_version": "rcs_v1",
            "content_type": "application/json",
            "data": {"input_parameters": params},
        },
    }
    return json.dumps(data)


@pytest.mark.parametrize("plugin", PLUGINS)
def test_plugin_executes(plugin: str, tmp_path: Path):
    script_path = Path("plugins") / plugin
    assert script_path.exists()

    params: dict[str, object] = {}
    if plugin == "gather-logs.sh":
        temp_log = tmp_path / "extra.log"
        temp_log.write_text("hello")
        params = {"extra_paths": [str(temp_log)]}
    if plugin == "restart-nomad.sh":
        params = {"check_jobs": True}

    result = subprocess.run(
        [str(script_path)],
        input=_base_input(params),
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["payload"]["result"] == "success"
    assert output["error"] is None

    if plugin == "gather-logs.sh":
        artifact_path = output["payload"]["output_data"]["artifact_path"]
        assert Path(artifact_path).exists()
        assert output["payload"]["output_data"]["entries_collected"] >= 1
    if plugin == "noop.sh":
        assert output["payload"]["output_data"]["input_parameters"] == params
