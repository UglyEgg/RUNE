# SPDX-FileCopyrightText: 2025 Richard Majewski <uglyegg@users.noreply.github.com>
# SPDX-License-Identifier: MPL-2.0

"""Top-level package for the RUNE orchestration framework."""

from importlib.metadata import version

__all__ = ["get_version"]


def get_version() -> str:
    """Return the installed package version."""
    try:
        return version("rune")
    except Exception:
        return "0.0.0"
