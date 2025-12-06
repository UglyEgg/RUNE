import json
import subprocess
from pathlib import Path

import pytest

PLUGINS = [
    "gather-logs.sh",
    "restart-docker.sh",
    "restart-nomad.sh",
    "noop.sh",
]


@pytest.mark.parametrize("plugin", PLUGINS)
def test_plugin_executes(plugin: str):
    script_path = Path("plugins") / plugin
    assert script_path.exists()
    result = subprocess.run(
        [str(script_path)], input="{}", text=True, capture_output=True, check=True
    )
    output = json.loads(result.stdout)
    assert output["payload"]["result"] == "success"
    assert output["error"] is None
