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
from dataclasses import asdict, dataclass
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
    category: str = "general"

    def render(self) -> str:
        prefix = f"[{self.severity}] {self.category}: {self.message}"
        if self.hint:
            return f"{prefix}\n  hint: {self.hint}"
        return prefix

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)


def git_available() -> bool:
    return run(["git", "--version"]).returncode == 0


def check_git_state(findings: list[Finding]) -> None:
    if not git_available():
        findings.append(Finding("WARN", "git is not available; skipping branch and worktree checks", category="git"))
        return

    status = run(["git", "status", "--porcelain"])
    if status.returncode != 0:
        findings.append(Finding("WARN", "could not read git status", status.stderr.strip(), category="git"))
        return
    if status.stdout.strip():
        findings.append(
            Finding(
                "WARN",
                "working tree has uncommitted changes",
                "commit, stash, or intentionally document them before closeout",
                category="git",
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
                    category="git",
                )
            )
        elif current:
            findings.append(Finding("INFO", f"current branch: {current}", category="git"))


def check_expected_files(findings: list[Finding]) -> None:
    expected = [
        ROOT / "me.md",
        ROOT / "docs" / "protocols" / "REPOSITORY_CLEANUP_PROTOCOL.md",
        ROOT / "skills" / "repo-cleanup" / "SKILL.md",
        VERIFY_SCRIPT,
    ]
    for path in expected:
        if not path.exists():
            findings.append(Finding("BLOCKER", f"expected cleanup file is missing: {path.relative_to(ROOT)}", category="files"))


def load_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None


def check_hyperkanban(findings: list[Finding]) -> None:
    if not HYPERKANBAN_STATE.exists():
        findings.append(Finding("INFO", "HyperKanban state not found; skipping HyperKanban cleanup checks", category="hyperkanban"))
        return
    if not HYPERKANBAN_PACKET.exists():
        findings.append(Finding("BLOCKER", "HyperKanban state exists but packet.txt is missing", category="hyperkanban"))

    validator = ROOT / "scripts" / "validate_hyperkanban.py"
    if validator.exists():
        result = run([sys.executable, str(validator.relative_to(ROOT)), str(HYPERKANBAN_STATE.relative_to(ROOT))])
        if result.returncode != 0:
            findings.append(
                Finding(
                    "BLOCKER",
                    "HyperKanban validation failed",
                    (result.stderr or result.stdout).strip(),
                    category="hyperkanban",
                )
            )
        else:
            findings.append(Finding("INFO", "HyperKanban validation passed", category="hyperkanban"))

    state = load_json(HYPERKANBAN_STATE)
    if not state:
        findings.append(Finding("BLOCKER", "HyperKanban state could not be parsed as JSON", category="hyperkanban"))
        return
    for card in state.get("cards", []):
        card_id = card.get("id", "<unknown>")
        coords = card.get("coords", {})
        contract_required = card.get("test_contract", {}).get("required") or card.get("doc_contract", {}).get("required")
        if coords.get("state") == "done" and contract_required:
            if not card.get("evidence_paths") and not card.get("open_exceptions"):
                findings.append(Finding("BLOCKER", f"done card lacks evidence or exception: {card_id}", category="hyperkanban"))
        if coords.get("state") == "blocked" and not card.get("blocked_reason"):
            findings.append(Finding("WARN", f"blocked card has no blocked_reason: {card_id}", category="hyperkanban"))


def check_docs(findings: list[Finding]) -> None:
    readme = ROOT / "README.md"
    status = ROOT / "plan" / "STATUS.md"
    if not readme.exists():
        findings.append(Finding("WARN", "README.md is missing", category="docs"))
    if status.exists():
        text = status.read_text(encoding="utf-8", errors="replace")
        if "Known cleanup needed" in text or "in progress" in text.lower():
            findings.append(
                Finding(
                    "INFO",
                    "plan/STATUS.md contains cleanup/in-progress language",
                    "confirm this still reflects the current repository state",
                    category="docs",
                )
            )


def check_verify_script(findings: list[Finding]) -> None:
    if not VERIFY_SCRIPT.exists():
        findings.append(Finding("BLOCKER", "scripts/verify.sh is missing", category="verification"))
        return
    text = VERIFY_SCRIPT.read_text(encoding="utf-8", errors="replace")
    if "validate_hyperkanban.py" not in text and HYPERKANBAN_STATE.exists():
        findings.append(
            Finding(
                "WARN",
                "scripts/verify.sh does not appear to run HyperKanban validation",
                "consider adding python scripts/validate_hyperkanban.py orchestration/hyperkanban/state.json",
                category="verification",
            )
        )
    if "pytest" not in text:
        findings.append(Finding("WARN", "scripts/verify.sh does not appear to run pytest", category="verification"))


def summarize(findings: Iterable[Finding]) -> dict[str, int]:
    items = list(findings)
    return {
        "blockers": sum(1 for item in items if item.severity == "BLOCKER"),
        "warnings": sum(1 for item in items if item.severity == "WARN"),
        "info": sum(1 for item in items if item.severity == "INFO"),
        "total": len(items),
    }


def collect_findings(phase: str) -> list[Finding]:
    findings: list[Finding] = [Finding("INFO", f"cleanup phase: {phase}", category="run")]
    check_expected_files(findings)
    check_git_state(findings)
    check_hyperkanban(findings)
    check_verify_script(findings)
    check_docs(findings)
    return findings


def build_report(phase: str, findings: list[Finding]) -> dict:
    return {
        "phase": phase,
        "summary": summarize(findings),
        "findings": [finding.to_dict() for finding in findings],
    }


def render_text(report: dict) -> str:
    lines = ["Repository cleanup audit", "========================"]
    findings = [Finding(**item) for item in report["findings"]]
    lines.extend(finding.render() for finding in findings)
    summary = report["summary"]
    lines.extend(
        [
            "------------------------",
            f"summary: {summary['blockers']} blockers, {summary['warnings']} warnings, {summary['info']} info",
        ]
    )
    return "\n".join(lines) + "\n"


def write_output(text: str, out: Path | None) -> None:
    if out is None:
        print(text, end="")
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"wrote cleanup report: {out}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a non-destructive repository cleanup audit.")
    parser.add_argument("--phase", choices=["before", "after"], default="before")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--out", type=Path, help="Optional path to write the cleanup report")
    args = parser.parse_args(argv)

    findings = collect_findings(args.phase)
    report = build_report(args.phase, findings)
    if args.format == "json":
        rendered = json.dumps(report, indent=2) + "\n"
    else:
        rendered = render_text(report)
    write_output(rendered, args.out)
    return 1 if report["summary"]["blockers"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
