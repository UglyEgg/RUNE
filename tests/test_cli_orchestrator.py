import json

from rune.rune_cli import main


def test_run_command_outputs_json(capsys):
    args = ["run", "noop", "--node", "localhost", "--param", "foo=bar"]
    exit_code = main(args)
    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["payload"]["result"] == "success"
    assert output["payload"]["output_data"]["action"] == "noop"
    assert output["payload"]["output_data"]["node"] == "localhost"
    assert output["payload"]["output_data"]["input_parameters"] == {"foo": "bar"}


def test_pretty_output_format(capsys):
    args = ["run", "noop", "--node", "n1", "--output", "pretty"]
    exit_code = main(args)
    assert exit_code == 0
    output_text = capsys.readouterr().out
    assert "\n  " in output_text
    data = json.loads(output_text)
    assert data["payload"]["result"] == "success"
