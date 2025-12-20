# Style guide

This guide defines coding and documentation conventions for RUNE. It is written for Python 3.13+ development with modern tooling and a bias toward correctness, maintainability, and operational safety.

## Language baseline

- **Minimum Python:** 3.13
- **Supported Python:** the project should remain compatible with the latest stable CPython release where practical.
- **Typing:** all new code should be type annotated. Prefer types that are enforced by tooling (not comments).

## Formatting and linting

### Formatting

Use **Ruff formatter** as the single source of formatting truth.

```bash
ruff format .
```

### Linting

Use **Ruff** for linting. Treat new lint warnings as failures in CI.

```bash
ruff check .
```

General expectations:

- No unused imports, variables, or unreachable code.
- No implicit optional (`Optional[...]`) ambiguity. Use `| None`.
- No bare `except:`. Catch the narrowest exception type possible.
- No `print()` in library code. Use logging. (CLI output is an exception.)

## Type checking

Use a static type checker (recommended: **Pyright**) in CI and locally.

Principles:

- Prefer **precise types** over `Any`.
- Use `Protocol` and structural typing for interfaces where it improves testability.
- Use `TypedDict` for JSON-like payloads when a full model class is unnecessary.
- Use `TypeAlias` for repeated complex types.

Examples:

```python
from __future__ import annotations

from typing import TypeAlias, TypedDict

TraceId: TypeAlias = str

class RcsRouting(TypedDict):
    event_type: str
    target_module: str

def parse_trace_id(value: str) -> TraceId:
    return value
```

## Imports

Follow these rules:

- Group imports: standard library, third-party, local.
- One import per line where it improves diff readability.
- Prefer `from collections.abc import Iterable, Mapping` over importing ABCs from `typing`.
- Prefer absolute imports inside the package unless relative imports improve clarity within a subpackage.

Ruff can enforce ordering.

## Naming conventions

- Modules: `snake_case.py`
- Classes: `CapWords`
- Functions and variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private internals: prefix with `_` to indicate non-public API.

## Code structure

### Prefer explicit boundaries

RUNE is protocol-first. Code should reflect this:

- Validate inputs at boundaries (CLI parsing, protocol parsing, plugin output parsing).
- Keep execution side effects contained and observable.
- Keep orchestration logic (decisions) separate from transport logic (how commands run).

### Dataclasses and immutability

- Use `@dataclass(slots=True)` for lightweight data containers.
- Prefer immutability for values passed between layers where it reduces accidental mutation.

```python
from dataclasses import dataclass

@dataclass(slots=True, frozen=True)
class ActionRequest:
    action: str
    node: str
```

### Paths and files

- Use `pathlib.Path` for filesystem operations.
- When writing files, write atomically where feasible (write to temp, then replace).

## Errors and exceptions

- Raise exceptions for programmer errors and invariant violations.
- For recoverable operational failures (remote host unreachable, plugin failure), convert to the project’s structured error protocol at the boundary where the failure is reported.
- Never swallow exceptions silently.
- Do not use exceptions for normal control flow.

Avoid overly broad patterns:

```python
# Avoid
try:
    ...
except Exception:
    ...
```

Prefer narrow handling:

```python
try:
    ...
except FileNotFoundError as e:
    ...
```

## Logging and observability

- Use the standard library `logging` module for all non-CLI output.
- Logs must be structured enough to support troubleshooting:
  - include node, action, and trace id where available
  - include exception context with `logger.exception(...)` when handling failures
- Never log secrets (tokens, private keys, full command lines containing credentials).

## Subprocess and remote execution safety

If invoking local commands (including SSH/SSM wrappers):

- Prefer `subprocess.run([...], check=True, text=True, capture_output=True)` with a list of args.
- Avoid `shell=True` unless there is a documented and reviewed need.
- Set timeouts for network and long-running operations.
- Sanitize or validate any user-provided arguments before constructing commands.

## Concurrency and async

If using asyncio:

- Prefer `asyncio.TaskGroup` for structured concurrency.
- Ensure tasks are awaited or managed. Do not spawn orphan tasks.
- Use timeouts and cancellation handling for remote operations.

## Documentation

### Docstrings

Use docstrings for public functions, public classes, and non-trivial internal functions.

- Follow PEP 257 conventions.
- Keep the first line as a single-sentence summary.
- Document side effects and failure modes.

Example:

```python
def run_action(action: str, node: str) -> None:
    """Execute an action against a node.

    Raises:
        ValueError: If the action name is invalid.
        RuntimeError: If execution fails after retries.
    """
```

### Markdown docs

- Prefer short sections with direct headings.
- Avoid duplicating protocol details across multiple pages. Link to canonical references.
- Use code fences for all examples; keep examples minimal and correct.

## Testing

Use **pytest** for unit and integration tests.

Expectations:

- Tests should be deterministic and not depend on external infrastructure unless explicitly marked as integration tests.
- Prefer dependency injection and fakes over patch-heavy tests.
- Validate both success and failure paths for protocol parsing and plugin execution.

Suggested commands:

```bash
pytest
pytest -q
```

## Tooling and automation

Recommended baseline:

- `ruff` for formatting and linting
- `pyright` (or equivalent) for type checking
- `pytest` for tests
- `pre-commit` to enforce checks before commit

Example pre-commit tools:

```bash
pre-commit install
pre-commit run --all-files
```

## Summary

- Format with Ruff.
- Lint with Ruff.
- Type check with Pyright.
- Test with pytest.
- Keep boundaries explicit, validate inputs early, and produce observable behavior.
