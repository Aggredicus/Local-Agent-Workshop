#!/usr/bin/env python3
"""
Local Agent Workshop dependency auditor.

Adapted from the dependency-auditor design in alirezarezvani/claude-skills.
Source path: claude-skills-2-main/engineering/skills/dependency-auditor/
License: MIT
Copyright (c) 2025 Alireza Rezvani

Local changes:
- local manifest review only
- no package installation or updates
- no live advisory lookups
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

SUPPORTED_MANIFESTS = {
    "package.json",
    "requirements.txt",
    "requirements-dev.txt",
    "pyproject.toml",
    "go.mod",
}

BROAD_SPECIFIERS = ("*", "latest")
VERSION_PREFIXES = ("^", "~", ">=", ">", "<=", "<")


@dataclass
class Dependency:
    name: str
    version: str
    ecosystem: str
    source_path: str
    group: str = "dependencies"


@dataclass
class Finding:
    severity: str
    message: str
    path: str
    line: int | None = None
    category: str = "dependency"
    recommendation: str = ""


def iter_manifests(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.name in SUPPORTED_MANIFESTS:
            yield path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def scan_package_json(path: Path, root: Path) -> tuple[list[Dependency], list[Finding]]:
    rel = str(path.relative_to(root))
    deps: list[Dependency] = []
    findings: list[Finding] = []
    try:
        data = load_json(path)
    except json.JSONDecodeError as exc:
        return [], [Finding("high", f"package.json could not be parsed: {exc}", rel, exc.lineno, "manifest", "Fix JSON syntax.")]

    if not data.get("license"):
        findings.append(Finding("medium", "package.json is missing license metadata.", rel, None, "license", "Add a license field or document why it is omitted."))

    for group in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        entries = data.get(group, {}) or {}
        if not isinstance(entries, dict):
            findings.append(Finding("medium", f"{group} should be an object.", rel, None, "manifest", "Use a dependency object keyed by package name."))
            continue
        for name, version in entries.items():
            version_str = str(version)
            deps.append(Dependency(name, version_str, "npm", rel, group))
            findings.extend(check_version(name, version_str, rel, group))
    return deps, findings


def scan_requirements(path: Path, root: Path) -> tuple[list[Dependency], list[Finding]]:
    rel = str(path.relative_to(root))
    deps: list[Dependency] = []
    findings: list[Finding] = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith(("-r ", "--requirement")):
            findings.append(Finding("info", "Nested requirements file reference found.", rel, line_no, "manifest", "Confirm nested requirement files are included in review."))
            continue
        if line.startswith(("-e ", "git+", "http://", "https://")):
            findings.append(Finding("high", "Non-index or direct source dependency reference found.", rel, line_no, "source", "Review direct source dependencies manually."))
        match = re.match(r"([A-Za-z0-9_.-]+)\s*([<>=!~]=?\s*.+)?$", line)
        if match:
            name = match.group(1)
            version = (match.group(2) or "").replace(" ", "") or "unpinned"
            deps.append(Dependency(name, version, "python", rel, "requirements"))
            findings.extend(check_version(name, version, rel, "requirements", line_no))
    return deps, findings


def scan_pyproject(path: Path, root: Path) -> tuple[list[Dependency], list[Finding]]:
    rel = str(path.relative_to(root))
    text = path.read_text(encoding="utf-8", errors="replace")
    deps: list[Dependency] = []
    findings: list[Finding] = []
    if re.search(r"^license\s*=", text, flags=re.MULTILINE) is None:
        findings.append(Finding("medium", "pyproject.toml has no top-level license field detected.", rel, None, "license", "Document project license metadata if applicable."))
    for line_no, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip().strip(",")
        dep_match = re.match(r'"([A-Za-z0-9_.-]+)([^"/]*)"', line)
        if dep_match and any(token in line for token in (">=", "==", "~=")):
            name = dep_match.group(1)
            version = dep_match.group(2).strip() or "declared"
            deps.append(Dependency(name, version, "python", rel, "pyproject"))
            findings.extend(check_version(name, version, rel, "pyproject", line_no))
    return deps, findings


def scan_go_mod(path: Path, root: Path) -> tuple[list[Dependency], list[Finding]]:
    rel = str(path.relative_to(root))
    deps: list[Dependency] = []
    findings: list[Finding] = []
    in_require = False
    for line_no, raw in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        line = raw.strip()
        if line.startswith("replace "):
            findings.append(Finding("medium", "go.mod replace directive found.", rel, line_no, "source", "Review replace directives before release."))
        if line.startswith("require ("):
            in_require = True
            continue
        if in_require and line == ")":
            in_require = False
            continue
        if line.startswith("require "):
            parts = line.split()
            if len(parts) >= 3:
                deps.append(Dependency(parts[1], parts[2], "go", rel, "require"))
        elif in_require:
            parts = line.split()
            if len(parts) >= 2 and not parts[0].startswith("//"):
                deps.append(Dependency(parts[0], parts[1], "go", rel, "require"))
    return deps, findings


def check_version(name: str, version: str, rel: str, group: str, line: int | None = None) -> list[Finding]:
    findings: list[Finding] = []
    normalized = version.strip().lower()
    if not normalized or normalized == "unpinned":
        findings.append(Finding("medium", f"{name} is not pinned to a version.", rel, line, "version", f"Pin or constrain {name} intentionally."))
    if normalized in BROAD_SPECIFIERS:
        findings.append(Finding("high", f"{name} uses broad version specifier `{version}`.", rel, line, "version", f"Replace {version} with an intentional version range or pin."))
    elif normalized.startswith(VERSION_PREFIXES):
        findings.append(Finding("info", f"{name} uses a flexible version specifier `{version}`.", rel, line, "version", "Confirm this range is intentional."))
    return findings


def scan_manifest(path: Path, root: Path) -> tuple[list[Dependency], list[Finding]]:
    if path.name == "package.json":
        return scan_package_json(path, root)
    if path.name in {"requirements.txt", "requirements-dev.txt"}:
        return scan_requirements(path, root)
    if path.name == "pyproject.toml":
        return scan_pyproject(path, root)
    if path.name == "go.mod":
        return scan_go_mod(path, root)
    return [], []


def build_report(root: Path, run_id: str, command: list[str]) -> dict:
    manifests = list(iter_manifests(root))
    dependencies: list[Dependency] = []
    findings: list[Finding] = []

    if not manifests:
        findings.append(Finding("medium", "No supported dependency manifests found.", str(root), None, "manifest", "Add support for the ecosystem or confirm no dependencies are declared."))

    for manifest in manifests:
        deps, file_findings = scan_manifest(manifest, root)
        dependencies.extend(deps)
        findings.extend(file_findings)

    verdict = "pass"
    if any(f.severity in {"critical", "high"} for f in findings):
        verdict = "fail"
    elif any(f.severity == "medium" for f in findings):
        verdict = "review"

    return {
        "skill": "dependency-auditor",
        "run_id": run_id,
        "mode": "analysis",
        "input_summary": {
            "target_path": str(root),
            "manifests_scanned": [str(p.relative_to(root)) for p in manifests],
            "dependency_count": len(dependencies),
            "verdict": verdict,
        },
        "findings": [asdict(f) for f in findings],
        "artifacts": [],
        "risks": [
            "Manifest-only review cannot prove transitive dependency safety.",
            "Live advisory lookups and package-manager execution are intentionally skipped in v1.0.",
        ],
        "recommendations": [
            "Use ecosystem-specific advisory tooling in a separately approved step when needed.",
            "Review high findings before release or merge.",
        ],
        "evidence": {
            "commands_run": [" ".join(command)],
            "skipped_checks": [
                "No package installation was performed.",
                "No package update was performed.",
                "No live advisory service was queried.",
                "Lockfile parsing is not implemented in v1.0.",
            ],
            "source_paths": [str(root)],
            "dependencies": [asdict(dep) for dep in dependencies],
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Review local dependency manifests and emit a Local Agent Workshop skill report.")
    parser.add_argument("path", help="Local project directory to review.")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Emit JSON to stdout.")
    parser.add_argument("--out", help="Optional output path for JSON report.")
    parser.add_argument("--run-id", default=None, help="Run identifier. Defaults to a timestamp.")
    parser.add_argument("--strict", action="store_true", help="Return non-zero when verdict is review or fail.")
    args = parser.parse_args(argv)

    root = Path(args.path).resolve()
    if not root.exists() or not root.is_dir():
        print(f"Target path is not a directory: {root}", file=sys.stderr)
        return 2

    run_id = args.run_id or time.strftime("%Y%m%d-%H%M%S")
    report = build_report(root, run_id=run_id, command=sys.argv)
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
