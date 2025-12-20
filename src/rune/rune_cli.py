"""Command-line interface entry point for RUNE."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from typing import Any

from rune.orchestrator import list_actions, run_action


def _build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the CLI."""

    parser = argparse.ArgumentParser(description="RUNE orchestration CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run an orchestration action")
    run_parser.add_argument("action", help="Action name")
    run_parser.add_argument(
        "--node",
        required=True,
        help="Target node hostname or identifier",
    )
    run_parser.add_argument(
        "--use-ssm",
        action="store_true",
        help="Use SSM transport instead of SSH",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate only without execution",
    )
    run_parser.add_argument(
        "--output",
        choices=["json", "pretty"],
        default="json",
        help="Output formatting",
    )
    run_parser.add_argument(
        "--param",
        action="append",
        dest="params",
        metavar="KEY=VALUE",
        help="Input parameters passed to the action (repeatable)",
    )

    list_parser = subparsers.add_parser("list-actions", help="List registered actions")
    list_parser.add_argument(
        "--output",
        choices=["json", "pretty"],
        default="pretty",
        help="Output formatting",
    )

    return parser


def _parse_params(raw_params: list[str] | None) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if not raw_params:
        return params

    for entry in raw_params:
        if "=" not in entry:
            raise argparse.ArgumentTypeError(f"Invalid parameter '{entry}', expected KEY=VALUE")
        key, value = entry.split("=", maxsplit=1)
        params[key] = value
    return params


def _print_output(data: dict[str, Any], mode: str) -> None:
    if mode == "pretty":
        print(json.dumps(data, indent=2))
    else:
        print(json.dumps(data))


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:  # argparse uses SystemExit for validation errors
        if exc.code and exc.code != 0:
            return 2
        raise

    if args.command == "list-actions":
        actions = [
            {**asdict(action), "plugin_path": str(action.plugin_path)}
            for action in list_actions()
        ]
        _print_output({"actions": actions}, args.output)
        return 0

    try:
        params = _parse_params(args.params)
    except argparse.ArgumentTypeError as exc:
        parser.print_usage()
        print(f"rune: error: {exc}", file=sys.stderr)
        return 2

    result = run_action(
        action=args.action,
        node=args.node,
        use_ssm=bool(args.use_ssm),
        dry_run=bool(args.dry_run),
        params=params,
    )

    _print_output(result.to_dict(), args.output)
    if result.status in {"success", "dry_run"}:
        return 0
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
