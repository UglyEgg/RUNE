# SPDX-FileCopyrightText: 2025 Richard Majewski <uglyegg@users.noreply.github.com>
# SPDX-License-Identifier: MPL-2.0

"""SSH transport stub for plugin execution."""

from __future__ import annotations

import json
from typing import Dict

from rune.models import PluginRequest, PluginResponse


class SSHTransport:
    """Simplified SSH transport that returns stubbed plugin output."""

    def run_plugin(self, action: str, node: str, request: PluginRequest) -> PluginResponse:
        """Pretend to execute a remote plugin over SSH and return a stubbed response."""

        payload: Dict[str, object] = {
            "transport": "ssh",
            "action": action,
            "node": node,
            "input_parameters": request.payload.get("input_parameters", {}),
            "raw_request": json.loads(json.dumps(request.to_dict())),  # ensure JSON-safe copy
        }
        return PluginResponse.success(output_data=payload, metadata=request.message_metadata,
                                      observability=request.observability)
