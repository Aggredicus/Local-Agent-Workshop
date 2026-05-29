#!/usr/bin/env python3
"""Non-destructive repository cleanup audit.

This script is intentionally local and conservative. It checks for common
repository hygiene issues before and after work, but it does not delete files,
close PRs, delete branches, or mutate protected state.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
HYPERKANBAN_STATE = ROOT / "orchestration" / "hyperkanban" / "state.json"
HYPERKANBAN_PACKET = ROOT / "orchestration" / "hyperkanban" / "packet.txt"
VERIFY_SCRIPT = ROOT / "scripts" / "verify.sh"


@dataclass
class Finding:
    severity: str
    message: str
    hint: str = ""

    def render(self) -> str:
        if self.hint:
            return f"[{self.severity}] {self.message}\n  hint: {self.hint}"
        return f"[{self.severity}] {self.message}"


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)


def git_available() -> bool:
    return run(["git", "--version"]).returncode == 0


def check_git_state(findings: list[Finding]) -> None:
    if not git_available():
        findings.append(Finding("WARN", "git is not available; skipping branch and worktree checks"))
        return

    status = run(["git", "status", "--porcelain"])
    if status.returncode != 0:
        findings.append(Finding("WARN", "could not read git status", status.stderr.strip()))
        return
    if status.stdout.strip():
        findings.append(
            Finding(
                "WARN",
                "working tree has uncommitted changes",
                "commit, stash, or intentionally document them before closeout",
            )
        )

    branch = run(["git", "branch", "--show-current"])
    if branch.returncode == 0:
        current = branch.stdout.strip()
        if current in {"main", "develop"}:
            findings.append(
                Finding(
                    "WARN",
                    f"current branch is protected/integration branch: {current}",
                    "use an agent/* branch for implementation work",
                )
            )
        elif current:
            findings.append(Finding("INFO", f"current branch: {current}"))


def check_expected_files(findings: list[Finding]) -> None:
    expected = [
        ROOT / "me.md",
        ROOT / "docs" / "protocols" / "REPOSITORY_CLEANUP_PROTOCOL.md",
        ROOT / "skills" / "repo-cleanup" / "SKILL.md",
        VERIFY_SCRIPT,
    ]
    for path in expected:
        if not path.exists():
            findings.append(Finding("BLOCKER", f"expected cleanup file is missing: {path.relative_to(ROOT)}"))


def load_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None


def check_hyperkanban(findings: list[Finding]) -> None:
    if not HYPERKANBAN_STATE.exists():
        findings.append(Finding("INFO", "HyperKanban state not found; skipping HyperKanban cleanup checks"))
        return
    if not HYPERKANBAN_PACKET.exists():
        findings.append(Finding("BLOCKER", "HyperKanban state exists but packet.txt is missing"))

    validator = ROOT / "scripts" / "validate_hyperkanban.py"
    if validator.exists():
        result = run([sys.executable, str(validator.relative_to(ROOT)), str(HYPERKANBAN_STATE.relative_to(ROOT))])
        if result.returncode != 0:
            findings.append(
                Finding(
                    "BLOCKER",
                    "HyperKanban validation failed",
                    (result.stderr or result.stdout).strip(),
                )
            )
        else:
            findings.append(Finding("INFO", "HyperKanban validation passed"))

    state = load_json(HYPERKANBAN_STATE)
    if not state:
        findings.append(Finding("BLOCKER", "HyperKanban state could not be parsed as JSON"))
        return
    for card in state.get("cards", []):
        card_id = card.get("id", "<unknown>")
        coords = card.get("coords", {})
        if coords.get("state") == "done" and (card.get("test_contract", {}).get("required") or card.get("doc_contract", {}).get("required")):
            if not card.get("evidence_paths") and not card.get("open_exceptions"):
                findings.append(Finding("BLOCKER", f"done card lacks evidence or exception: {card_id}"))
        if coords.get("state") == "blocked" and not card.get("blocked_reason"):
            findings.append(Finding("WARN", f"blocked card has no blocked_reason: {card_id}"))


def check_docs(findings: list[Finding]) -> None:
    readme = ROOT / "README.md"
    status = ROOT / "plan" / "STATUS.md"
    if not readme.exists():
        findings.append(Finding("WARN", "README.md is missing"))
    if status.exists():
        text = status.read_text(encoding="utf-8", errors="replace")
        if "Known cleanup needed" in text or "in progress" in text.lower():
            findings.append(
                Finding(
                    "INFO",
                    "plan/STATUS.md contains cleanup/in-progress language",
                    "confirm this still reflects the current repository state",
                )
            )


def check_verify_script(findings: list[Finding]) -> None:
    if not VERIFY_SCRIPT.exists():
        findings.append(Finding("BLOCKER", "scripts/verify.sh is missing"))
        return
    text = VERIFY_SCRIPT.read_text(encoding="utf-8", errors="replace")
    if "validate_hyperkanban.py" not in text and HYPERKANBAN_STATE.exists():
        findings.append(
            Finding(
                "WARN",
                "scripts/verify.sh does not appear to run HyperKanban validation",
                "consider adding python scripts/validate_hyperkanban.py orchestration/hyperkanban/state.json",
            )
        )
    if "pytest" not in text:
        findings.append(Finding("WARN", "scripts/verify.sh does not appear to run pytest"))


def summarize(findings: Iterable[Finding]) -> tuple[int, int, int]:
    items = list(findings)
    blockers = sum(1 for item in items if item.severity == "BLOCKER")
    warnings = sum(1 for item in items if item.severity == "WARN")
    info = sum(1 for item in items if item.severity == "INFO")
    return blockers, warnings, info


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a non-destructive repository cleanup audit.")
    parser.add_argument("--phase", choices=["before", "after"], default="before")
    args = parser.parse_args(argv)

    findings: list[Finding] = []
    findings.append(Finding("INFO", f"cleanup phase: {args.phase}"))
    check_expected_files(findings)
    check_git_state(findings)
    check_hyperkanban(findings)
    check_verify_script(findings)
    check_docs(findings)

    print("Repository cleanup audit")
    print("========================")
    for finding in findings:
        print(finding.render())

    blockers, warnings, info = summarize(findings)
    print("------------------------")
    print(f"summary: {blockers} blockers, {warnings} warnings, {info} info")

    return 1 if blockers else 0


if __name__ == "__main__":
    raise SystemExit(main())
