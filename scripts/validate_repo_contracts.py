#!/usr/bin/env python3
"""Read-only repository contract validation for Local Agent Workshop.

This script intentionally uses only the Python standard library so it can run in
local development, CI, and constrained Proxmox/local-runner environments.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
SCHEMA_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_\-.]*$")
VALID_STATUSES = {"planned", "draft", "active", "deprecated", "retired"}
REQUIRED_REGISTRY_FIELDS = {
    "schema_version",
    "artifact_type",
    "generated_by",
    "schemas",
}
REQUIRED_RECORD_FIELDS = {
    "schema_id",
    "name",
    "version",
    "path",
    "owner_protocol",
    "status",
    "compatible_versions",
    "example_paths",
    "validation_command",
    "migration_notes",
}


@dataclass
class Finding:
    severity: str
    category: str
    message: str
    hint: str = ""

    def render(self) -> str:
        line = f"[{self.severity}] {self.category}: {self.message}"
        if self.hint:
            line += f"\n  hint: {self.hint}"
        return line


def load_json(path: Path) -> tuple[Any | None, list[Finding]]:
    if not path.exists():
        return None, [
            Finding(
                "ERROR",
                "registry",
                f"missing JSON file: {path}",
                "Create the file or pass the correct --schema-registry path.",
            )
        ]
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except json.JSONDecodeError as exc:
        return None, [
            Finding(
                "ERROR",
                "registry",
                f"invalid JSON in {path}: {exc}",
                "Fix JSON syntax before running semantic validation.",
            )
        ]


def validate_registry_shape(registry: Any) -> list[Finding]:
    findings: list[Finding] = []
    if not isinstance(registry, dict):
        return [Finding("ERROR", "registry", "registry root must be a JSON object")]

    missing = sorted(REQUIRED_REGISTRY_FIELDS - set(registry))
    for field in missing:
        findings.append(Finding("ERROR", "registry", f"missing required field: {field}"))

    if registry.get("artifact_type") != "schema_registry":
        findings.append(
            Finding("ERROR", "registry", "artifact_type must be schema_registry")
        )

    schema_version = registry.get("schema_version")
    if not isinstance(schema_version, str) or not SEMVER_RE.match(schema_version):
        findings.append(
            Finding(
                "ERROR",
                "registry",
                "schema_version must use MAJOR.MINOR.PATCH format",
            )
        )

    schemas = registry.get("schemas")
    if not isinstance(schemas, list) or not schemas:
        findings.append(
            Finding("ERROR", "registry", "schemas must be a non-empty array")
        )

    return findings


def validate_schema_records(registry: dict[str, Any], root: Path) -> list[Finding]:
    findings: list[Finding] = []
    schemas = registry.get("schemas", [])
    seen_ids: set[str] = set()

    if not isinstance(schemas, list):
        return findings

    for index, record in enumerate(schemas):
        label = f"schemas[{index}]"
        if not isinstance(record, dict):
            findings.append(Finding("ERROR", "registry", f"{label} must be an object"))
            continue

        missing = sorted(REQUIRED_RECORD_FIELDS - set(record))
        for field in missing:
            findings.append(
                Finding("ERROR", "registry", f"{label} missing required field: {field}")
            )

        schema_id = record.get("schema_id")
        if not isinstance(schema_id, str) or not SCHEMA_ID_RE.match(schema_id):
            findings.append(
                Finding(
                    "ERROR",
                    "registry",
                    f"{label} has invalid schema_id: {schema_id!r}",
                    "Use lowercase letters, digits, underscores, hyphens, or periods.",
                )
            )
        elif schema_id in seen_ids:
            findings.append(
                Finding("ERROR", "registry", f"duplicate schema_id: {schema_id}")
            )
        else:
            seen_ids.add(schema_id)

        version = record.get("version")
        if not isinstance(version, str) or not SEMVER_RE.match(version):
            findings.append(
                Finding(
                    "ERROR",
                    "registry",
                    f"{schema_id or label} version must use MAJOR.MINOR.PATCH format",
                )
            )

        status = record.get("status")
        if status not in VALID_STATUSES:
            findings.append(
                Finding(
                    "ERROR",
                    "registry",
                    f"{schema_id or label} has invalid status: {status!r}",
                )
            )

        path_value = record.get("path")
        if not isinstance(path_value, str) or not path_value.strip():
            findings.append(
                Finding("ERROR", "registry", f"{schema_id or label} path is required")
            )
            continue

        artifact_path = root / path_value
        if status != "planned" and not artifact_path.exists():
            findings.append(
                Finding(
                    "ERROR",
                    "registry",
                    f"{schema_id or label} path does not exist: {path_value}",
                    "Only planned schemas may point to missing future paths.",
                )
            )
        elif status == "planned" and not artifact_path.exists():
            findings.append(
                Finding(
                    "INFO",
                    "registry",
                    f"{schema_id or label} planned path not present yet: {path_value}",
                )
            )

        example_paths = record.get("example_paths")
        if not isinstance(example_paths, list):
            findings.append(
                Finding(
                    "ERROR",
                    "registry",
                    f"{schema_id or label} example_paths must be an array",
                )
            )
            example_paths = []

        if status == "active" and not example_paths:
            findings.append(
                Finding(
                    "ERROR",
                    "registry",
                    f"active schema {schema_id} must include at least one example path",
                )
            )

        for example_path in example_paths:
            if not isinstance(example_path, str):
                findings.append(
                    Finding(
                        "ERROR",
                        "registry",
                        f"{schema_id or label} example path must be a string",
                    )
                )
                continue
            if not (root / example_path).exists():
                severity = "WARN" if status == "planned" else "ERROR"
                findings.append(
                    Finding(
                        severity,
                        "registry",
                        f"{schema_id or label} example path does not exist: {example_path}",
                    )
                )

        migration_notes = record.get("migration_notes")
        if not isinstance(migration_notes, str) or not migration_notes.strip():
            findings.append(
                Finding(
                    "ERROR",
                    "registry",
                    f"{schema_id or label} migration_notes must be non-empty",
                )
            )

    return findings


def summarize(findings: list[Finding]) -> dict[str, int]:
    return {
        "errors": sum(1 for finding in findings if finding.severity == "ERROR"),
        "warnings": sum(1 for finding in findings if finding.severity == "WARN"),
        "info": sum(1 for finding in findings if finding.severity == "INFO"),
        "total": len(findings),
    }


def build_report(registry_path: Path, findings: list[Finding]) -> dict[str, Any]:
    return {
        "artifact_type": "repo_contract_validation_report",
        "validator": "scripts/validate_repo_contracts.py",
        "schema_registry": str(registry_path),
        "summary": summarize(findings),
        "findings": [asdict(finding) for finding in findings],
    }


def render_text(report: dict[str, Any]) -> str:
    lines = ["Repository contract validation", ""]
    summary = report["summary"]
    lines.append(
        f"SUMMARY: {summary['errors']} errors, {summary['warnings']} warnings, {summary['info']} info"
    )
    lines.append(f"schema_registry: {report['schema_registry']}")
    if report["findings"]:
        lines.append("")
        for finding in report["findings"]:
            lines.append(Finding(**finding).render())
    return "\n".join(lines) + "\n"


def write_output(content: str, path: Path | None) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"wrote validation report: {path}")


def validate(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    root = Path(args.root).resolve()
    registry_path = (root / args.schema_registry).resolve()
    registry, findings = load_json(registry_path)
    if registry is not None:
        findings.extend(validate_registry_shape(registry))
        if isinstance(registry, dict):
            findings.extend(validate_schema_records(registry, root))
    report = build_report(registry_path.relative_to(root), findings)
    return report, 1 if report["summary"]["errors"] else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root. Defaults to current working directory.",
    )
    parser.add_argument(
        "--schema-registry",
        default="schemas/schema-registry.json",
        help="Path to schema registry, relative to --root.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format.",
    )
    parser.add_argument("--out", help="Optional path to write the rendered report.")
    args = parser.parse_args(argv)

    report, exit_code = validate(args)
    if args.format == "json":
        rendered = json.dumps(report, indent=2) + "\n"
    else:
        rendered = render_text(report)

    print(rendered, end="")
    write_output(rendered, Path(args.out) if args.out else None)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
