#!/usr/bin/env python3
"""Read-only repository contract validation for Local Agent Workshop.

This script intentionally uses only the Python standard library so it can run in
local development, CI, and constrained Proxmox/local-runner environments.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path, PureWindowsPath
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
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except FileNotFoundError:
        return None, [Finding("ERROR", "registry", f"missing JSON file: {path}", "Pass an existing repository-relative --schema-registry path.")]
    except json.JSONDecodeError as exc:
        return None, [Finding("ERROR", "registry", f"invalid JSON at line {exc.lineno}, column {exc.colno}", "Fix JSON syntax before semantic validation.")]
    except (OSError, UnicodeError):
        return None, [Finding("ERROR", "registry", f"cannot read UTF-8 JSON file: {path}", "Check file type, permissions and encoding.")]


def repository_file(root: Path, value: Any, label: str, findings: list[Finding]) -> Path | None:
    """Resolve a portable relative path without following a link outside root."""
    try:
        if (not isinstance(value, str) or not value.strip() or '\x00' in value
                or value.startswith(('/', '\\')) or PureWindowsPath(value).drive
                or '..' in PureWindowsPath(value).parts):
            raise ValueError
        path = (root / value).resolve()
        path.relative_to(root)
        if path.exists() and not path.is_file():
            raise ValueError
        return path
    except (ValueError, OSError, RuntimeError):
        findings.append(Finding("ERROR", "registry", f"{label} must name a repository-relative file inside the root", "Directories, traversal and escaping links are rejected."))
        return None


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
    if not isinstance(schema_version, str) or not SEMVER_RE.fullmatch(schema_version):
        findings.append(
            Finding(
                "ERROR",
                "registry",
                "schema_version must use MAJOR.MINOR.PATCH format",
            )
        )

    if not isinstance(registry.get('generated_by'), str) or not registry['generated_by'].strip():
        findings.append(Finding('ERROR', 'registry', 'generated_by must be a non-empty string'))
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
        if not isinstance(schema_id, str) or not SCHEMA_ID_RE.fullmatch(schema_id):
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
        if not isinstance(version, str) or not SEMVER_RE.fullmatch(version):
            findings.append(
                Finding(
                    "ERROR",
                    "registry",
                    f"{schema_id or label} version must use MAJOR.MINOR.PATCH format",
                )
            )

        status = record.get("status")
        if not isinstance(status, str) or status not in VALID_STATUSES:
            findings.append(
                Finding(
                    "ERROR",
                    "registry",
                    f"{schema_id or label} has invalid status: {status!r}",
                )
            )

        for field in ('name', 'owner_protocol', 'validation_command', 'migration_notes'):
            if not isinstance(record.get(field), str) or not record[field].strip():
                findings.append(Finding('ERROR', 'registry', f'{label}.{field} must be a non-empty string'))
        for field in ('compatible_versions', 'example_paths'):
            values = record.get(field)
            if (not isinstance(values, list) or not all(isinstance(v, str) for v in values)
                    or len(values) != len(set(values))):
                findings.append(Finding('ERROR', 'registry', f'{label}.{field} must be an array of unique strings'))

        path_value = record.get("path")
        artifact_path = repository_file(root, path_value, f'{label}.path', findings)
        if artifact_path is not None and status != "planned" and not artifact_path.is_file():
            findings.append(
                Finding(
                    "ERROR",
                    "registry",
                    f"{schema_id or label} path does not exist: {path_value}",
                    "Only planned schemas may point to missing future paths.",
                )
            )
        elif artifact_path is not None and status == "planned" and not artifact_path.is_file():
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
            example_file = repository_file(root, example_path, f'{label}.example_paths', findings)
            if example_file is not None and not example_file.is_file():
                severity = "WARN" if status == "planned" else "ERROR"
                findings.append(
                    Finding(
                        severity,
                        "registry",
                        f"{schema_id or label} example path does not exist: {example_path}",
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


def render_text(report: dict[str, Any], *, quiet: bool = False) -> str:
    lines = ["Repository contract validation", ""]
    summary = report["summary"]
    lines.append(
        f"SUMMARY: {summary['errors']} errors, {summary['warnings']} warnings, {summary['info']} info"
    )
    lines.append(f"schema_registry: {report['schema_registry']}")
    if report["findings"]:
        lines.append("")
        for finding in report["findings"]:
            if not quiet or finding["severity"] != "INFO":
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
    findings: list[Finding] = []
    registry_path = repository_file(root, args.schema_registry, 'schema_registry', findings)
    if registry_path is None:
        report = build_report(Path(args.schema_registry), findings)
        return report, 1
    registry, load_findings = load_json(registry_path)
    findings.extend(load_findings)
    if not load_findings:
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
    parser.add_argument("--quiet", action="store_true", help="Omit informational details; keep warnings, errors and summary")
    args = parser.parse_args(argv)

    report, exit_code = validate(args)
    if args.format == "json":
        rendered = json.dumps(report, indent=2) + "\n"
    else:
        rendered = render_text(report, quiet=args.quiet)

    print(rendered, end="")
    write_output(rendered, Path(args.out) if args.out else None)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
