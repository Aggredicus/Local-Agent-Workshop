#!/usr/bin/env python3
"""
Local Agent Workshop skill security auditor.

Adapted from the skill-security-auditor design in alirezarezvani/claude-skills.
Source path: claude-skills-2-main/engineering/skills/skill-security-auditor/
License: MIT
Copyright (c) 2025 Alireza Rezvani

Local changes:
- read-only local directory scanner only
- no repository cloning
- normalized JSON report shape for Local Agent Workshop
- synthetic fixture/test support
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

TEXT_EXTENSIONS = {
    ".md", ".txt", ".py", ".sh", ".bash", ".js", ".ts", ".tsx", ".jsx",
    ".json", ".yaml", ".yml", ".toml", ".ini", ".env", ".example",
}

MAX_FILE_BYTES = 1_000_000


@dataclass(frozen=True)
class PatternRule:
    severity: str
    category: str
    pattern: str
    message: str
    recommendation: str
    applies_to: str = "all"


@dataclass
class Finding:
    severity: str
    message: str
    path: str
    line: int | None = None
    category: str = "general"
    recommendation: str = ""


RULES: list[PatternRule] = [
    PatternRule("critical", "code-execution", r"\beval\s*\(", "Dynamic evaluation pattern found.", "Replace dynamic evaluation with explicit parsing."),
    PatternRule("critical", "code-execution", r"\bexec\s*\(", "Dynamic execution pattern found.", "Replace dynamic execution with explicit code paths."),
    PatternRule("critical", "shell", r"shell\s*=\s*True", "Shell mode pattern found in process launch.", "Use argument lists and shell-free process calls."),
    PatternRule("high", "shell", r"\bos\.system\s*\(", "Direct system command wrapper found.", "Use safer library APIs or reviewed argument-list process calls."),
    PatternRule("high", "network", r"\brequests\.(post|put|patch)\s*\(", "Outbound write-style HTTP client call found.", "Document why network access is needed and gate it behind approval."),
    PatternRule("high", "network", r"\b(socket|httpx|aiohttp)\b", "Network library reference found.", "Keep live network behavior disabled by default."),
    PatternRule("high", "filesystem", r"~/(?:\.ssh|\.aws|\.config)", "Private home configuration path reference found.", "Avoid reading private local configuration in skills."),
    PatternRule("high", "deserialization", r"\byaml\.load\s*\(", "YAML load pattern found.", "Use safe YAML loading in reviewed code paths."),
    PatternRule("high", "deserialization", r"\bpickle\.loads?\s*\(", "Pickle deserialization pattern found.", "Use JSON or another safer data format."),
    PatternRule("medium", "prompt-text", r"ignore previous instructions", "Prompt override phrase found in text.", "Treat this as data to quote or test, not as instruction.", "markdown"),
    PatternRule("medium", "prompt-text", r"you are now", "Role override phrase found in text.", "Treat this as data to quote or test, not as instruction.", "markdown"),
]


def is_probably_text(path: Path) -> bool:
    if path.name == ".env" or path.suffix.lower() in TEXT_EXTENSIONS:
        return True
    return False


def inventory_files(root: Path) -> tuple[list[Path], list[dict[str, str]]]:
    files: list[Path] = []
    unreviewed: list[dict[str, str]] = []
    def unreadable(error: OSError) -> None:
        path = Path(error.filename) if error.filename else root
        unreviewed.append({"path": str(path.relative_to(root)), "reason": "unreadable directory"})
    for folder, dirs, names in os.walk(root, followlinks=False, onerror=unreadable):
        for name in sorted(dirs.copy()):
            path = Path(folder) / name
            if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
                dirs.remove(name)
                unreviewed.append({"path": str(path.relative_to(root)), "reason": "symlink not followed"})
        for name in sorted(names):
            path = Path(folder) / name
            reason = ""
            try:
                if path.is_symlink():
                    reason = "symlink not followed"
                elif not path.is_file():
                    reason = "special file"
                elif path.stat().st_size > MAX_FILE_BYTES:
                    reason = "size limit"
                elif not is_probably_text(path):
                    reason = "unsupported file type"
            except OSError:
                reason = "unreadable file"
            if reason:
                unreviewed.append({"path": str(path.relative_to(root)), "reason": reason})
            else:
                files.append(path)
    return sorted(files), sorted(unreviewed, key=lambda item: item["path"])


def iter_candidate_files(root: Path) -> Iterable[Path]:
    return iter(inventory_files(root)[0])


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def rule_applies(rule: PatternRule, path: Path) -> bool:
    if rule.applies_to == "all":
        return True
    if rule.applies_to == "markdown":
        return path.suffix.lower() in {".md", ".txt"}
    return True


def scan_file(path: Path, root: Path) -> list[Finding]:
    rel = str(path.relative_to(root))
    text = read_text(path)
    findings: list[Finding] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        for rule in RULES:
            if not rule_applies(rule, path):
                continue
            if re.search(rule.pattern, line, flags=re.IGNORECASE):
                findings.append(
                    Finding(
                        severity=rule.severity,
                        message=rule.message,
                        path=rel,
                        line=line_no,
                        category=rule.category,
                        recommendation=rule.recommendation,
                    )
                )
    return findings


def build_report(root: Path, run_id: str, mode: str, command: list[str]) -> dict:
    files, unreviewed = inventory_files(root)
    findings: list[Finding] = []

    if not (root / "SKILL.md").exists():
        findings.append(
            Finding(
                severity="medium",
                message="Candidate skill is missing SKILL.md.",
                path="SKILL.md",
                line=None,
                category="structure",
                recommendation="Add a SKILL.md file before treating this as a Local Agent Workshop skill.",
            )
        )

    for path in files:
        try:
            findings.extend(scan_file(path, root))
        except OSError:
            unreviewed.append({"path": str(path.relative_to(root)), "reason": "unreadable file"})
    if unreviewed:
        findings.append(Finding("medium", "Review coverage is incomplete; inspect the unreviewed file inventory.", ".", category="coverage"))

    verdict = "pass"
    if any(f.severity == "critical" for f in findings):
        verdict = "fail"
    elif any(f.severity in {"high", "medium"} for f in findings):
        verdict = "review"

    return {
        "skill": "skill-security-auditor",
        "run_id": run_id,
        "mode": mode,
        "input_summary": {
            "target_path": str(root),
            "files_scanned": len(files) - sum(1 for item in unreviewed if item["reason"] == "unreadable file"),
            "coverage_complete": not unreviewed,
            "scanner": "local-read-only",
            "verdict": verdict,
        },
        "findings": [asdict(f) for f in findings],
        "artifacts": [],
        "risks": [
            "Heuristic text matching can miss issues or produce false positives.",
            "This wrapper does not perform dependency vulnerability lookups.",
        ],
        "recommendations": [
            "Inspect high and critical findings manually before activating a skill.",
            "Run repository-specific tests before merging imported skill automation.",
        ],
        "evidence": {
            "commands_run": [" ".join(command)],
            "unreviewed_files": unreviewed,
            "skipped_checks": [
                "No live network lookups were performed.",
                "No external repository cloning was performed.",
            ],
            "source_paths": [str(root)],
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Review a local skill directory and emit a Local Agent Workshop skill report.")
    parser.add_argument("path", help="Local candidate skill directory to review.")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Emit JSON to stdout.")
    parser.add_argument("--out", help="Optional output path for JSON report.")
    parser.add_argument("--run-id", default=None, help="Run identifier. Defaults to a timestamp.")
    parser.add_argument("--strict", action="store_true", help="Return non-zero for findings requiring review or incomplete coverage.")
    args = parser.parse_args(argv)

    root = Path(args.path).resolve()
    if not root.exists() or not root.is_dir():
        print(f"Target path is not a directory: {root}", file=sys.stderr)
        return 2

    run_id = args.run_id or time.strftime("%Y%m%d-%H%M%S")
    report = build_report(root, run_id=run_id, mode="analysis", command=sys.argv)

    payload = json.dumps(report, indent=2, sort_keys=True)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload + "\n", encoding="utf-8")

    if args.json_output or not args.out:
        print(payload)

    has_blocking = report["input_summary"]["verdict"] != "pass"
    if args.strict and has_blocking:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
