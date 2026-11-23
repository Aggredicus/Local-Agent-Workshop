"""Isolated NCM Lab CLI: no network calls and no heavyweight dependencies."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from workshop.ncm_lab import NcmLabError, audit_trace, load_json, save_json, validate_benchmarks


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    ncm = subparsers.add_parser("ncm", help="NCM research: anchor gates and offline comparison validation")
    cmds = ncm.add_subparsers(dest="ncm_command")
    audit = cmds.add_parser("audit", help="Block name/number/constraint changes between planning levels")
    audit.add_argument("--contract", type=Path, required=True)
    audit.add_argument("--trace", type=Path, required=True)
    audit.add_argument("--output", type=Path, help="Optional JSON evidence report")
    check = cmds.add_parser("validate-runs", help="Validate comparability and provenance of benchmark JSON")
    check.add_argument("--input", type=Path, required=True)
    check.add_argument("--output", type=Path, help="Optional JSON validation report")


def handle(args: argparse.Namespace) -> int:
    try:
        if args.ncm_command == "audit":
            result = audit_trace(load_json(args.contract), load_json(args.trace))
            status = 0 if result["passed"] else 1
        elif args.ncm_command == "validate-runs":
            result = validate_benchmarks(load_json(args.input))
            status = 0
        else:
            print("Choose 'audit' or 'validate-runs'.")
            return 2
        if args.output:
            save_json(args.output, result)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return status
    except (NcmLabError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"NCM Lab: {exc}")
        return 2
