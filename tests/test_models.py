from __future__ import annotations

from rune.models import StructuredError, build_message_metadata, build_observability


def test_structured_error_to_dict_includes_details():
    error = StructuredError(code=400, message="bad", details={"field": "value"})
    serialized = error.to_dict()
    assert serialized["code"] == 400
    assert serialized["details"]["field"] == "value"


def test_observability_and_metadata_shapes():
    metadata = build_message_metadata()
    observability = build_observability()
    assert metadata["version"] == "1.0"
    assert "trace_id" in observability and "span_id" in observability
