# Python Style Guide

## Overview

This project follows PEP-8 with modern Python best practices and some intentional deviations documented below.

---

## Core Standards

### Line Length

**Maximum:** 99 characters

**Rationale:**

- Modern standard (black/ruff default)
- Better for modern displays and IDEs
- Balances readability with practicality
- Reduces unnecessary line breaks

**Note:** This is an intentional deviation from strict PEP-8 (79 characters) but aligns with modern Python community practices and tooling defaults.

---

### Type Hints

**Style:** Python 3.10+ syntax with `from __future__ import annotations`

#### Modern Type Syntax

```python
from __future__ import annotations

# Use built-in generics (not typing.List, typing.Dict, etc.)
def process_items(items: list[str]) -> dict[str, int]:
    """Process a list of items and return counts."""
    ...

# Use union operator for optional types (not typing.Optional)
def get_value(key: str) -> str | None:
    """Return value or None if not found."""
    ...

# Use union operator for unions (not typing.Union)
def parse_data(data: str | bytes) -> dict[str, Any]:
    """Parse string or bytes data."""
    ...

# Use tuple for fixed-length sequences
def get_coordinates() -> tuple[float, float]:
    """Return x, y coordinates."""
    ...
```

#### Type Hints Best Practices

- **Always use type hints** on public function parameters and return types
- **Use `from __future__ import annotations`** at the top of modules
- **Prefer built-in types** over `typing` module equivalents
- **Keep `typing` imports** only for special types (Any, Callable, TypedDict, etc.)
- **Annotate complex types** to improve code clarity
- **Use type aliases** for complex or repeated types

```python
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

# Type alias for clarity
PathLike = str | Path

def process_file(path: PathLike, callback: Callable[[str], Any]) -> None:
    """Process a file with a callback function."""
    ...
```

---

### Docstrings

**Format:** PEP-257 compliant with Google-style parameter documentation

#### Module Docstrings

```python
"""Short module description.

Longer description providing more context about the module's purpose,
main functionality, and usage patterns.
"""
```

#### Function Docstrings

```python
def function_name(arg1: str, arg2: int) -> bool:
    """Short description of what the function does.

    Longer description if needed, explaining the function's behavior,
    side effects, or important implementation details.

    Args:
        arg1: Description of first argument
        arg2: Description of second argument

    Returns:
        Description of return value

    Raises:
        ValueError: When arg2 is negative
        FileNotFoundError: When file doesn't exist
    """
    ...
```

#### Class Docstrings

```python
class ClassName:
    """Short description of the class.

    Longer description explaining the class purpose, main responsibilities,
    and usage patterns.

    Attributes:
        attr1: Description of attribute
        attr2: Description of attribute
    """

    def __init__(self, param: str) -> None:
        """Initialize the class.

        Args:
            param: Description of parameter
        """
        ...
```

---

### Imports

**Order:**

1. Standard library imports
2. Third-party package imports
3. Local application imports

**Grouping:** Separate each group with a blank line

**Style:** One import per line for clarity

```python
# Standard library
import os
import sys
from pathlib import Path

# Third-party
import click
import requests

# Local
from .core import process_file
from .data import load_data
```

---

### Naming Conventions

| Type           | Convention              | Example                  |
| -------------- | ----------------------- | ------------------------ |
| **Functions**  | `snake_case`            | `def process_data():`    |
| **Variables**  | `snake_case`            | `user_name = "John"`     |
| **Constants**  | `UPPER_SNAKE_CASE`      | `MAX_SIZE = 100`         |
| **Classes**    | `PascalCase`            | `class UserProfile:`     |
| **Exceptions** | `PascalCase`            | `class ValidationError:` |
| **Private**    | `_leading_underscore`   | `def _internal_func():`  |
| **Protected**  | `_leading_underscore`   | `self._protected_attr`   |
| **Dunder**     | `__double_underscore__` | `__init__`, `__str__`    |

---

### Code Organization

#### Module Structure

```python
#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 Author Name <email@example.com>
# SPDX-License-Identifier: LICENSE-ID

"""Module docstring."""

from __future__ import annotations

# Imports (grouped as above)
import os
from pathlib import Path

# Constants
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

# Type aliases
PathLike = str | Path

# Classes
class MyClass:
    ...

# Functions
def my_function():
    ...

# Main execution
if __name__ == "__main__":
    ...
```

#### Function Length

- **Target:** <20-30 lines per function
- **Rationale:** Easier to understand, test, and maintain
- **Refactor** long functions into smaller, focused helper functions

#### Single Responsibility

- Each function should do **one thing** well
- Each class should have **one reason to change**
- Extract complex logic into separate functions

---

### Modern Python Practices

#### String Formatting

**Prefer f-strings:**

```python
# Good
name = "Alice"
message = f"Hello, {name}!"

# Avoid
message = "Hello, %s!" % name
message = "Hello, {}!".format(name)
```

#### Path Handling

**Prefer pathlib.Path:**

```python
from pathlib import Path

# Good
path = Path("data") / "file.txt"
if path.exists():
    content = path.read_text()

# Avoid
import os
path = os.path.join("data", "file.txt")
if os.path.exists(path):
    with open(path) as f:
        content = f.read()
```

#### Context Managers

**Always use `with` for resources:**

```python
# Good
with open("file.txt") as f:
    content = f.read()

# Avoid
f = open("file.txt")
content = f.read()
f.close()
```

#### Comprehensions

**Use when readable:**

```python
# Good - clear and concise
squares = [x**2 for x in range(10)]
evens = [x for x in numbers if x % 2 == 0]

# Avoid - too complex
result = [
    process(x, y, z)
    for x in items
    for y in x.subitems
    for z in y.subsubitems
    if condition(x, y, z)
]
```

#### Enums

**Use for fixed sets:**

```python
from enum import Enum

class Status(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
```

---

### Error Handling

#### EAFP vs LBYL

**Prefer EAFP** (Easier to Ask Forgiveness than Permission):

```python
# Good - EAFP
try:
    value = config[key]
except KeyError:
    value = default

# Avoid - LBYL
if key in config:
    value = config[key]
else:
    value = default
```

#### Specific Exceptions

**Catch specific exceptions:**

```python
# Good
try:
    data = json.loads(text)
except json.JSONDecodeError as exc:
    logger.error(f"Invalid JSON: {exc}")
    raise

# Avoid
try:
    data = json.loads(text)
except Exception:
    pass
```

#### Exception Context

**Preserve exception context:**

```python
# Good
try:
    result = risky_operation()
except ValueError as exc:
    msg = f"Operation failed: {exc}"
    raise RuntimeError(msg) from exc

# Avoid
try:
    result = risky_operation()
except ValueError:
    raise RuntimeError("Operation failed")
```

---

## Tooling

### Formatter

**black** (line-length=99)

```bash
# Format all code
black src/ tests/

# Check formatting
black --check src/ tests/
```

### Linters

**ruff** (comprehensive linting)

```bash
# Lint code
ruff check src/ tests/

# Auto-fix issues
ruff check --fix src/ tests/
```

**isort** (import sorting)

```bash
# Sort imports
isort src/ tests/

# Check import order
isort --check-only src/ tests/
```

### Type Checker

**mypy** (static type checking)

```bash
# Type check code
mypy src/

# Strict mode
mypy --strict src/
```

---

## Running Checks

### Quick Check

```bash
# Format, lint, and test
make quick-check
```

### Individual Checks

```bash
# Format code
make format

# Run linters
make lint

# Run type checker
mypy src/

# Run tests
make test

# Run all checks
make check
```

---

## Configuration

### pyproject.toml

```toml
[tool.black]
line-length = 99
target-version = ['py39']

[tool.ruff]
line-length = 99
target-version = "py39"
select = ["E", "F", "I", "N", "W"]

[tool.isort]
profile = "black"
line_length = 99

[tool.mypy]
python_version = "3.9"
strict = true
warn_return_any = true
warn_unused_configs = true
```

---

## Pre-commit Hooks

Install pre-commit hooks to automatically check code before committing:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## References

### PEPs (Python Enhancement Proposals)

- [PEP-8: Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [PEP-257: Docstring Conventions](https://peps.python.org/pep-0257/)
- [PEP-484: Type Hints](https://peps.python.org/pep-0484/)
- [PEP-585: Type Hinting Generics In Standard Collections](https://peps.python.org/pep-0585/)
- [PEP-604: Allow writing union types as X | Y](https://peps.python.org/pep-0604/)
- [PEP-563: Postponed Evaluation of Annotations](https://peps.python.org/pep-0563/)

### Tools

- [Black: The uncompromising code formatter](https://black.readthedocs.io/)
- [Ruff: An extremely fast Python linter](https://docs.astral.sh/ruff/)
- [mypy: Static type checker](https://mypy.readthedocs.io/)
- [isort: Import sorter](https://pycqa.github.io/isort/)

---

## Summary

This style guide ensures:

- ✅ Consistent, readable code
- ✅ Modern Python practices
- ✅ Strong type safety
- ✅ Maintainable codebase
- ✅ Automated quality checks

**Key Principles:**

1. Clarity over cleverness
2. Explicit over implicit
3. Simple over complex
4. Tested over untested
5. Documented over undocumented

---
