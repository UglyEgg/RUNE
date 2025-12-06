from rune.mediator import Mediator
from rune.models import PluginRequest
from rune.transport_ssm import SSMTransport


def test_mediator_uses_ssh_by_default():
    mediator = Mediator()
    request = PluginRequest()
    response = mediator.execute(action="noop", node="localhost", request=request)
    assert response.is_success
    assert response.payload["output_data"]["transport"] == "ssh"


def test_ssm_transport_is_placeholder():
    ssm = SSMTransport()
    request = PluginRequest()
    response = ssm.run_plugin(action="noop", node="node-1", request=request)
    assert not response.is_success
    assert response.error is not None
    assert response.error.code == 501
