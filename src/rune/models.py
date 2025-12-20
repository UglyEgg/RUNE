"""Shared dataclasses and typed objects used across the RUNE framework."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

__all__ = [
    "ActionMetadata",
    "StructuredError",
    "TransportResult",
    "MediatorResult",
    "OrchestrationResult",
    "build_message_metadata",
    "build_observability",
]


@dataclass(slots=True)
class ActionMetadata:
    """Describe a registered action and where to find its plugin implementation."""

    name: str
    description: str
    plugin_path: Path


@dataclass(slots=True)
class StructuredError:
    """Error envelope conforming to the Error Protocol Specification."""

    code: int
    message: str
    details: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize the error for JSON emission."""

        return {"code": self.code, "message": self.message, "details": self.details}


@dataclass(slots=True)
class TransportResult:
    """Raw output from a transport call without protocol interpretation."""

    stdout: str
    stderr: str
    exit_code: int


@dataclass(slots=True)
class MediatorResult:
    """Normalized output from the Local Mediation Module."""

    status: str
    action: str
    node: str
    transport: str
    plugin_output: dict[str, Any] | None
    error: StructuredError | None

    def to_dict(self) -> dict[str, Any]:
        """Convert the mediator result into an EPS-style dictionary."""

        return {
            "status": self.status,
            "action": self.action,
            "node": self.node,
            "transport": self.transport,
            "plugin_output": self.plugin_output,
            "error": self.error.to_dict() if self.error else None,
        }


@dataclass(slots=True)
class OrchestrationResult:
    """Public result returned by the Lifecycle Orchestration Module."""

    status: str
    action: str
    node: str
    transport: str | None
    message_metadata: dict[str, Any]
    observability: dict[str, Any]
    plugin_output: dict[str, Any] | None
    error: StructuredError | None

    def to_dict(self) -> dict[str, Any]:
        """Serialize the orchestration result using EPS field names."""

        return {
            "status": self.status,
            "action": self.action,
            "node": self.node,
            "transport": self.transport,
            "message_metadata": self.message_metadata,
            "observability": self.observability,
            "plugin_output": self.plugin_output,
            "error": self.error.to_dict() if self.error else None,
        }


def build_message_metadata() -> dict[str, Any]:
    """Construct the Runtime Communication Specification message metadata."""

    return {
        "version": "1.0",
        "message_id": str(uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def build_observability() -> dict[str, Any]:
    """Construct observability tracing identifiers."""

    return {"trace_id": str(uuid4()), "span_id": str(uuid4())}
