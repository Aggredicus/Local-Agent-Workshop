"""Isolated NCM Lab CLI: no network calls and no heavyweight dependencies."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from workshop.ncm_lab import NcmLabError, audit_trace, load_json, save_json, validate_benchmarks
from workshop.ncm_upstream import run_tinystories


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
    upstream = cmds.add_parser("run-tinystories", help="Run pinned upstream NCM code (explicit opt-in)")
    upstream.add_argument("--root", required=True, type=Path, help="Manually verified upstream NCM checkout")
    upstream.add_argument("--expected-commit", required=True)
    upstream.add_argument("--generator-sha256", required=True)
    upstream.add_argument("--tokenizer-sha256", required=True)
    upstream.add_argument("--python", type=Path, required=True, help="Interpreter in a separate NCM virtual environment")
    upstream.add_argument("--samples", type=int, default=1)
    upstream.add_argument("--seed", type=int, default=42)
    upstream.add_argument("--timeout", type=int, default=120)
    upstream.add_argument("--output", type=Path, required=True, help="New JSONL output path; parent must exist")
    upstream.add_argument("--report", type=Path, required=True, help="New audit report path; parent must exist")
    upstream.add_argument("--acknowledge-third-party-code", action="store_true")



def handle(args: argparse.Namespace) -> int:
    try:
        if args.ncm_command == "audit":
            result = audit_trace(load_json(args.contract), load_json(args.trace))
            status = 0 if result["passed"] else 1
        elif args.ncm_command == "validate-runs":
            result = validate_benchmarks(load_json(args.input))
            status = 0
        elif args.ncm_command == "run-tinystories":
            result = run_tinystories(args)
            status = 0 if result["status"] == "completed" else 1
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
