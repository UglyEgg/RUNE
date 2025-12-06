# Makefile for RUNE

# Configure runtime paths
export UV_CACHE_DIR := $(CURDIR)/.uv-cache
PYTHON := $(CURDIR)/.venv/bin/python

RUN := $(PYTHON) -m
RUN_DEV := $(PYTHON) -m
PYTEST_COV_ARGS := --cov=src --cov-report=html --cov-report=term-missing
LINT_PATHS := src tests
FORMAT_PATHS := src tests
CLEAN_FIND_EXTS := pyc pyo orig rej
CLEAN_CACHE_DIRS := .pytest_cache .mypy_cache .tox htmlcov .coverage .ruff_cache
CLEAN_ALL_EXTRA := .uv uv.lock
TYPECHECK_PATHS := src
PRE_COMMIT := pre_commit

BLACK := black
RUFF := ruff
ISORT := isort
MYPY := mypy
MKDOCS := mkdocs

BLACK_ARGS := --line-length=99
BLACK_LINT_ARGS := --check --line-length=99
RUFF_ARGS := check
ISORT_ARGS := --profile=black --line-length=99
ISORT_LINT_ARGS := --check-only --profile=black --line-length=99

TEMPLATE_SKIP_install := 1
TEMPLATE_SKIP_install_dev := 1
TEMPLATE_SKIP_info := 1

.PHONY: sync sync-dev build publish publish-test serve-docs mkdocs-deploy bump-version dev-setup quick-check release-check info update-deps lock ci-install ci-test ci-check show-outdated tree clean format lint test check

install:
	uv pip install -e .

install-dev:
	uv sync --extra dev

sync:
	uv sync

sync-dev:
	uv sync --extra dev

bump-version:
	@if [ -n "$(version)" ]; then \
		uv run --extra dev python scripts/bump_version.py --set $(version); \
	else \
		uv run --extra dev python scripts/bump_version.py --part $${part:-patch}; \
	fi
	@uv run --extra dev hatch version

build: clean
	./scripts/build.sh

publish-test:
	./scripts/release.sh --repository testpypi

publish:
	./scripts/release.sh

info:
	@echo "Python version:"
	@$(PYTHON) --version
	@if command -v uv >/dev/null 2>&1; then \
		echo; \
		echo "UV version:"; \
		uv --version; \
		echo; \
		echo "Installed packages (uv pip list):"; \
		uv pip list; \
	else \
		echo; \
		echo "UV not found on PATH – skipping uv diagnostics."; \
	fi
	@echo
	@echo "Project info:"
	@PYTHONPATH=src $(PYTHON) -c "import importlib.util; spec = importlib.util.find_spec('rune'); print(f'rune module: {spec.origin}' if spec and spec.origin else 'rune not installed')"

dev-setup: install-dev pre-commit-install
	@echo "Development environment is ready!"
	@echo "Run 'make help' to see available commands"

quick-check: format lint test

release-check: clean check build

update-deps:
	uv sync --upgrade

lock:
	uv lock

ci-install:
	uv sync --frozen

ci-test:
	uv run pytest --cov=src --cov-report=xml

ci-check:
	uv run black --check src tests
	uv run isort --check-only src tests
	uv run ruff check src tests
	uv run mypy src
	uv run pytest --cov=src --cov-report=xml

show-outdated:
	uv pip list --outdated

tree:
	tree -I '__pycache__|*.pyc|*.pyo|.git|.pytest_cache|.mypy_cache|*.egg-info|build|dist|.venv|.uv'

serve-docs:
	$(MKDOCS) serve

mkdocs-deploy:
	$(MKDOCS) gh-deploy --clean

pre-commit-install:
	uv run pre-commit install

pre-commit-run:
	uv run pre-commit run --all-files

format:
	$(RUN_DEV) $(BLACK) $(BLACK_ARGS) $(FORMAT_PATHS)
	$(RUN_DEV) $(ISORT) $(ISORT_ARGS) $(FORMAT_PATHS)

lint:
	$(RUN_DEV) $(RUFF) $(RUFF_ARGS) $(LINT_PATHS)
	$(RUN_DEV) $(BLACK) $(BLACK_LINT_ARGS) $(FORMAT_PATHS)
	$(RUN_DEV) $(ISORT) $(ISORT_LINT_ARGS) $(FORMAT_PATHS)

typecheck:
	$(RUN_DEV) $(MYPY) $(TYPECHECK_PATHS)

test:
	$(RUN_DEV) pytest $(PYTEST_COV_ARGS)

test-fast:
	$(RUN_DEV) pytest

check: lint typecheck test

clean:
	@echo "Cleaning build artifacts..."
	@find . -name "*.pyc" -delete
	@find . -name "*.pyo" -delete
	@find . -name "*.pyd" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} +
	@find . -name "*.egg-info" -type d -exec rm -rf {} +
	@find . -name "*.egg" -type f -delete
	@find . -name "*.so" -type f -delete
	@rm -rf build/
	@rm -rf dist/
	@rm -rf .coverage
	@rm -rf htmlcov/
	@rm -rf .pytest_cache/
	@rm -rf .mypy_cache/
	@rm -rf .ruff_cache/

clean-all: clean
	@echo "Cleaning all files..."
	@rm -rf .venv/
	@rm -rf .uv/
	@rm -rf uv.lock
	@rm -rf .uv-cache/

help:
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
