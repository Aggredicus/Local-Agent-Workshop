#!/usr/bin/env python3
"""
Local Agent Workshop env secrets manager.

Adapted from the env-secrets-manager design in alirezarezvani/claude-skills.
Source path: claude-skills-2-main/engineering/skills/env-secrets-manager/
License: MIT
Copyright (c) 2025 Alireza Rezvani

Local changes:
- local dotenv-style review only
- no private value printing
- no credential rotation or cloud secret-store calls
- normalized JSON report shape for Local Agent Workshop
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

SUPPORTED_NAMES = {".env", ".env.local", ".env.example", ".env.sample", ".env.template"}
SUPPORTED_SUFFIXES = (".env.example", ".env.sample", ".env.template")
PLACEHOLDER_VALUES = {
    "",
    "changeme",
    "change-me",
    "example",
    "example-value",
    "placeholder",
    "todo",
    "your-value",
    "your_value",
    "replace-me",
    "replace_me",
}
SENSITIVE_KEY_HINTS = ("secret", "token", "password", "passwd", "private", "credential", "api_key", "apikey", "auth")
SUSPICIOUS_VALUE_RE = re.compile(r"^[A-Za-z0-9_./+=:-]{20,}$")


@dataclass
class EnvEntry:
    key: str
    value_redacted: str
    source_path: str
    line: int
    is_example: bool


@dataclass
class Finding:
    severity: str
    message: str
    path: str
    line: int | None = None
    category: str = "env"
    recommendation: str = ""


def is_supported_env_file(path: Path) -> bool:
    return path.name in SUPPORTED_NAMES or path.name.endswith(SUPPORTED_SUFFIXES)


def is_example_file(path: Path) -> bool:
    name = path.name.lower()
    return name.endswith((".example", ".sample", ".template")) or ".example" in name or ".sample" in name or ".template" in name


def display_path(path: Path, root: Path) -> str:
    """Render a path for reports without assuming it is inside root."""
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def iter_env_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if path.is_file() and is_supported_env_file(path):
            yield path


def redact(value: str) -> str:
    if value == "":
        return "<empty>"
    return "<redacted>"


def parse_env_file(path: Path, root: Path) -> tuple[list[EnvEntry], list[Finding]]:
    rel = display_path(path, root)
    entries: list[EnvEntry] = []
    findings: list[Finding] = []
    seen: dict[str, int] = {}
    example = is_example_file(path)

    for line_no, raw in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if "=" not in line:
            findings.append(Finding("low", "Non key-value line found in env file.", rel, line_no, "syntax", "Use KEY=value syntax or document custom parsing."))
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", key):
            findings.append(Finding("medium", f"Invalid env key syntax `{key}`.", rel, line_no, "syntax", "Use shell-compatible env key names."))
            continue
        if key in seen:
            findings.append(Finding("medium", f"Duplicate env key `{key}` found.", rel, line_no, "drift", "Keep only one value per key."))
        seen[key] = line_no
        entries.append(EnvEntry(key, redact(value), rel, line_no, example))

        key_l = key.lower()
        value_l = value.lower()
        if example and any(hint in key_l for hint in SENSITIVE_KEY_HINTS):
            if value_l not in PLACEHOLDER_VALUES and SUSPICIOUS_VALUE_RE.match(value):
                findings.append(Finding("high", f"Example/template file appears to contain a concrete value for `{key}`.", rel, line_no, "redaction", "Replace with a placeholder."))
        if (not example) and value and value_l in PLACEHOLDER_VALUES:
            findings.append(Finding("info", f"Runtime env file contains placeholder-like value for `{key}`.", rel, line_no, "drift", "Confirm this value is expected."))
    return entries, findings


def resolve_optional(root: Path, maybe_path: str | None) -> Path | None:
    if not maybe_path:
        return None
    path = Path(maybe_path)
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def compare_key_sets(example_path: Path, env_path: Path, root: Path) -> list[Finding]:
    example_entries, _ = parse_env_file(example_path, root)
    env_entries, _ = parse_env_file(env_path, root)
    example_keys = {entry.key for entry in example_entries}
    env_keys = {entry.key for entry in env_entries}
    rel_example = display_path(example_path, root)
    rel_env = display_path(env_path, root)
    findings: list[Finding] = []
    for key in sorted(example_keys - env_keys):
        findings.append(Finding("medium", f"`{key}` is documented in example/template but missing from env file.", rel_env, None, "drift", "Add locally or document optionality."))
    for key in sorted(env_keys - example_keys):
        findings.append(Finding("medium", f"`{key}` exists in env file but is missing from example/template.", rel_example, None, "drift", "Add placeholder to example/template if required."))
    return findings


def build_report(root: Path, run_id: str, command: list[str], example: str | None, env: str | None) -> dict:
    files = list(iter_env_files(root))
    entries: list[EnvEntry] = []
    findings: list[Finding] = []

    for path in files:
        file_entries, file_findings = parse_env_file(path, root)
        entries.extend(file_entries)
        findings.extend(file_findings)

    if not files:
        findings.append(Finding("medium", "No supported env files found.", str(root), None, "manifest", "Add an env example/template."))

    example_path = resolve_optional(root, example)
    env_path = resolve_optional(root, env)
    if example_path or env_path:
        if not example_path or not env_path:
            findings.append(Finding("medium", "Both --example and --env are required for drift comparison.", str(root), None, "drift", "Pass both paths."))
        elif not example_path.exists() or not env_path.exists():
            findings.append(Finding("high", "Comparison file path does not exist.", str(root), None, "drift", "Check paths."))
        else:
            findings.extend(compare_key_sets(example_path, env_path, root))

    verdict = "pass"
    if any(f.severity in {"critical", "high"} for f in findings):
        verdict = "fail"
    elif any(f.severity == "medium" for f in findings):
        verdict = "review"

    return {
        "skill": "env-secrets-manager",
        "run_id": run_id,
        "mode": "analysis",
        "input_summary": {
            "target_path": str(root),
            "files_scanned": [display_path(path, root) for path in files],
            "key_count": len(entries),
            "verdict": verdict,
        },
        "findings": [asdict(finding) for finding in findings],
        "artifacts": [],
        "risks": [
            "Dotenv-style parsing can miss project-specific config formats.",
            "All values are redacted; humans may need to inspect local files directly when safe.",
        ],
        "recommendations": [
            "Keep example/template files placeholder-only.",
            "Use explicit --example and --env comparison for drift review.",
        ],
        "evidence": {
            "commands_run": [" ".join(command)],
            "skipped_checks": [
                "No raw env values were printed.",
                "No env files were modified.",
                "No credential rotation was performed.",
                "No cloud secret store was queried.",
            ],
            "source_paths": [str(root)],
            "env_entries": [asdict(entry) for entry in entries],
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Review local env files and emit a redacted Local Agent Workshop skill report.")
    parser.add_argument("path", help="Local project directory to review.")
    parser.add_argument("--example", help="Optional example/template path for key comparison.")
    parser.add_argument("--env", help="Optional local env path for key comparison.")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Emit JSON to stdout.")
    parser.add_argument("--out", help="Optional output path for JSON report.")
    parser.add_argument("--run-id", default=None, help="Run identifier. Defaults to a timestamp.")
    parser.add_argument("--strict", action="store_true", help="Return non-zero when verdict is review or fail.")
    args = parser.parse_args(argv)

    root = Path(args.path).resolve()
    if not root.exists() or not root.is_dir():
        print(f"Target path is not a directory: {root}", file=sys.stderr)
        return 2

    report = build_report(root, args.run_id or time.strftime("%Y%m%d-%H%M%S"), sys.argv, args.example, args.env)
    payload = json.dumps(report, indent=2, sort_keys=True)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload + "\n", encoding="utf-8")
    if args.json_output or not args.out:
        print(payload)
    if args.strict and report["input_summary"]["verdict"] != "pass":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
