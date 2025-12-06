# SPDX-FileCopyrightText: 2025 Richard Majewski <uglyegg@users.noreply.github.com>
# SPDX-License-Identifier: MPL-2.0

"""Data models for RUNE orchestration messages and errors."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4


@dataclass(slots=True)
class MessageMetadata:
    """Metadata associated with plugin requests and responses."""

    version: str = "1.0"
    message_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    correlation_id: Optional[str] = None


@dataclass(slots=True)
class ObservabilityContext:
    """Trace identifiers to correlate calls across the system."""

    trace_id: str = field(default_factory=lambda: str(uuid4()))
    span_id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(slots=True)
class RuneError:
    """Structured error aligned with the RUNE Error Propagation Specification (EPS)."""

    code: int
    message: str
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the error to a dictionary."""
        return {"code": self.code, "message": self.message, "details": self.details}


@dataclass(slots=True)
class PluginRequest:
    """Payload delivered to remote plugins via stdin."""

    message_metadata: MessageMetadata = field(default_factory=MessageMetadata)
    payload: Dict[str, Any] = field(default_factory=lambda: {"input_parameters": {}})
    observability: ObservabilityContext = field(default_factory=ObservabilityContext)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the request into a JSON-serialisable dictionary."""
        return {
            "message_metadata": asdict(self.message_metadata),
            "payload": self.payload,
            "observability": asdict(self.observability),
        }


@dataclass(slots=True)
class PluginResponse:
    """Standardised plugin output following the Bash Plugin Communication Specification."""

    message_metadata: MessageMetadata
    payload: Optional[Dict[str, Any]]
    observability: ObservabilityContext
    error: Optional[RuneError] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert the response into a JSON-serialisable dictionary."""
        return {
            "message_metadata": asdict(self.message_metadata),
            "payload": self.payload,
            "observability": asdict(self.observability),
            "error": self.error.to_dict() if self.error else None,
        }

    @classmethod
    def success(cls, output_data: Dict[str, Any], metadata: Optional[MessageMetadata] = None,
                observability: Optional[ObservabilityContext] = None) -> "PluginResponse":
        """Create a successful plugin response."""
        metadata = metadata or MessageMetadata()
        observability = observability or ObservabilityContext()
        return cls(
            message_metadata=metadata,
            payload={"result": "success", "output_data": output_data},
            observability=observability,
            error=None,
        )

    @classmethod
    def failure(
        cls,
        error: RuneError,
        metadata: Optional[MessageMetadata] = None,
        observability: Optional[ObservabilityContext] = None,
    ) -> "PluginResponse":
        """Create a failed plugin response."""
        metadata = metadata or MessageMetadata()
        observability = observability or ObservabilityContext()
        return cls(
            message_metadata=metadata,
            payload=None,
            observability=observability,
            error=error,
        )

    @property
    def is_success(self) -> bool:
        """Return True when the response represents a successful execution."""
        return self.error is None and bool(self.payload)
