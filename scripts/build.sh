#!/bin/bash

set -euo pipefail

VERSION=$(python - <<'PY'
import tomllib, pathlib

data = tomllib.loads(pathlib.Path("pyproject.toml").read_text())
version = data.get("project", {}).get("version")
if not version:
    raise SystemExit("Unable to determine package version from pyproject.toml")
print(version)
PY
)

echo "Building spdx-headers package (version ${VERSION})…"

# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build source distribution and wheel
uv run --with build python -m build

# Verify metadata renders correctly on PyPI
uv run --with twine python -m twine check dist/*

echo "Build complete. Files in dist/:"
ls -la dist/
