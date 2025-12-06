#!/bin/bash

set -euo pipefail

REPOSITORY="pypi"

if [[ $# -gt 0 ]]; then
  case "$1" in
  --repository | -r)
    REPOSITORY="${2:-}"
    if [[ -z "$REPOSITORY" ]]; then
      echo "Error: --repository requires a value (e.g. pypi or testpypi)." >&2
      exit 1
    fi
    shift 2
    ;;
  *)
    echo "Usage: $0 [--repository pypi|testpypi]" >&2
    exit 1
    ;;
  esac
fi

# Ensure working tree is clean
if [[ -n "$(git status --porcelain)" ]]; then
  echo "Error: git working tree is dirty. Commit or stash changes before releasing." >&2
  exit 1
fi

VERSION_FILE="src/spdx_headers/_version.py"
if [[ ! -f "$VERSION_FILE" ]]; then
  cat <<'EOF' >&2
Error: src/spdx_headers/_version.py is missing.
Run `python scripts/bump_version.py --set <version>` (or reinstall the package)
to regenerate the version file before publishing.
EOF
  exit 1
fi

VERSION=$(
  python - <<'PY'
import pathlib, re

data = pathlib.Path("src/spdx_headers/_version.py").read_text()
match = re.search(r'__version__\s*=\s*version\s*=\s*"([^"]+)"', data)
if not match:
    raise SystemExit("Unable to determine package version from _version.py")
print(match.group(1))
PY
)

TAG="v${VERSION}"

if ! git rev-parse "$TAG" >/dev/null 2>&1; then
  echo "Error: expected git tag '$TAG' to exist. Create it before releasing." >&2
  exit 1
fi

if [[ "$(git rev-parse HEAD)" != "$(git rev-parse "$TAG")" ]]; then
  echo "Error: tag '$TAG' does not point at HEAD. Ensure you tagged the release commit." >&2
  exit 1
fi

echo "Running full build pipeline…"
./scripts/build.sh

echo "Uploading artifacts to ${REPOSITORY}…"
uv run --with twine python -m twine upload --repository "${REPOSITORY}" dist/*

echo "Release complete!"
