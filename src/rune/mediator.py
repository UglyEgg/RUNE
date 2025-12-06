# SPDX-FileCopyrightText: 2025 Richard Majewski <uglyegg@users.noreply.github.com>
# SPDX-License-Identifier: MPL-2.0

"""Mediator coordinating transport selection and plugin invocation."""

from __future__ import annotations

from typing import Optional

from rune.models import PluginRequest, PluginResponse
from rune.transport_ssh import SSHTransport
from rune.transport_ssm import SSMTransport


class Mediator:
    """Single mediation layer normalising transport behaviour."""

    def __init__(
        self,
        ssh_transport: Optional[SSHTransport] = None,
        ssm_transport: Optional[SSMTransport] = None,
    ) -> None:
        self.ssh_transport = ssh_transport or SSHTransport()
        self.ssm_transport = ssm_transport or SSMTransport()

    def execute(self, action: str, node: str, request: PluginRequest) -> PluginResponse:
        """Execute an action on a node, selecting the appropriate transport.

        For the MVP, SSH is always used while SSM remains a placeholder.
        """

        transport = self._select_transport(node)
        return transport.run_plugin(action=action, node=node, request=request)

    def _select_transport(self, node: str):
        """Choose the transport for a node.

        The MVP unconditionally picks SSH but provides a hook for future logic.
        """

        _ = node  # placeholder for routing heuristics
        return self.ssh_transport
