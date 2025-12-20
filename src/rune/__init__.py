"""RUNE orchestration framework."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

__all__ = ["__version__"]

try:
    __version__ = version("rune")
except PackageNotFoundError:  # pragma: no cover - during editable installs
    __version__ = "0.0.0"
