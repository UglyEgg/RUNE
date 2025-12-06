# SPDX-FileCopyrightText: 2025 Richard Majewski <uglyegg@users.noreply.github.com>
# SPDX-License-Identifier: MPL-2.0

"""Command-line interface entry point for RUNE."""

from __future__ import annotations

import argparse
import json
from typing import Dict, List, Optional

from rune.orchestrator import Orchestrator


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the CLI."""

    parser = argparse.ArgumentParser(description="RUNE orchestration CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run an orchestration action")
    run_parser.add_argument("action", help="Name of the action/plugin to execute")
    run_parser.add_argument("--node", required=True, help="Target node hostname or identifier")
    run_parser.add_argument(
        "--param",
        action="append",
        dest="params",
        metavar="KEY=VALUE",
        help="Input parameters passed to the action (repeatable)",
    )
    run_parser.add_argument(
        "--output",
        choices=["json", "pretty"],
        default="json",
        help="Output formatting mode",
    )
    return parser


def parse_params(raw_params: Optional[List[str]]) -> Dict[str, str]:
    """Parse repeated KEY=VALUE pairs into a dictionary."""

    params: Dict[str, str] = {}
    if not raw_params:
        return params

    for item in raw_params:
        if "=" not in item:
            raise argparse.ArgumentTypeError(f"Invalid parameter '{item}', expected KEY=VALUE")
        key, value = item.split("=", maxsplit=1)
        params[key] = value
    return params


def main(argv: Optional[List[str]] = None) -> int:
    """Entry point invoked by the console script."""

    parser = build_parser()
    args = parser.parse_args(argv)

    parameters = parse_params(args.params)
    orchestrator = Orchestrator()
    response = orchestrator.run_action(action=args.action, node=args.node, parameters=parameters)

    output = response.to_dict()
    if args.output == "pretty":
        print(json.dumps(output, indent=2))
    else:
        print(json.dumps(output))

    return 0 if response.is_success else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
