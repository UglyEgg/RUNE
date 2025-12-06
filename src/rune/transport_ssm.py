# SPDX-FileCopyrightText: 2025 Richard Majewski <uglyegg@users.noreply.github.com>
# SPDX-License-Identifier: MPL-2.0

"""Stub for an AWS SSM-based transport."""

from __future__ import annotations

from rune.models import PluginRequest, PluginResponse, RuneError


class SSMTransport:
    """Placeholder SSM transport that will be implemented in a future iteration."""

    def run_plugin(self, action: str, node: str, request: PluginRequest) -> PluginResponse:
        """Return a not-implemented error response for SSM calls."""

        error = RuneError(
            code=501,
            message="SSM transport is not yet implemented",
            details={"action": action, "node": node},
        )
        return PluginResponse.failure(error=error, metadata=request.message_metadata,
                                      observability=request.observability)
