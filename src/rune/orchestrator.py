# SPDX-FileCopyrightText: 2025 Richard Majewski <uglyegg@users.noreply.github.com>
# SPDX-License-Identifier: MPL-2.0

"""Orchestrator responsible for validating and dispatching actions."""

from __future__ import annotations

from typing import Any, Dict, Optional

from rune.mediator import Mediator
from rune.models import PluginRequest, PluginResponse


class Orchestrator:
    """Validate requests and coordinate plugin execution."""

    def __init__(self, mediator: Optional[Mediator] = None) -> None:
        self.mediator = mediator or Mediator()

    def run_action(
        self, action: str, node: str, parameters: Optional[Dict[str, Any]] = None
    ) -> PluginResponse:
        """Run the requested action on a remote node via the mediator.

        Args:
            action: Name of the plugin to execute.
            node: Target node identifier.
            parameters: Optional input parameters passed to the plugin.

        Returns:
            PluginResponse: Normalised plugin response.
        """

        request = PluginRequest(
            payload={"input_parameters": parameters or {}, "action": action, "node": node}
        )
        return self.mediator.execute(action=action, node=node, request=request)
