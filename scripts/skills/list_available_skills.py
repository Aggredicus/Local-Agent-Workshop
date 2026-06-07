#!/usr/bin/env python3
"""
List Local Agent Workshop skills by scanning skills/*/SKILL.md.

Read-only helper for /skill-discovery.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

GOVERNANCE_KEYWORDS = (
    "merge",
    "approval",
    "protected branch",
    "security",
    "secrets",
    "credential",
    "external skill",
    "import",
    "activate",
    "review",
)

KNOWN_GATE_SKILLS = {
    "/merge-review": ["merge", "pr review", "approval", "stacked pr"],
    "/skill-security-auditor": ["external skill", "import", "activate", "untrusted", "skill script"],
    "/dependency-auditor": ["dependency", "package", "license", "version", "manifest"],
    "/env-secrets-manager": ["env", ".env", "secret", "credential", "redaction", "config"],
}


def normalize_skill_name(name: str) -> str:
    name = name.strip()
    if not name:
        return name
    return name if name.startswith("/") else f"/{name}"


def strip_frontmatter(text: str) -> tuple[dict[str, str], str]:
    metadata: dict[str, str] = {}
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            for raw in parts[1].splitlines():
                if ":" not in raw:
                    continue
                key, value = raw.split(":", 1)
                metadata[key.strip().lower()] = value.strip().strip('"').strip("'")
            return metadata, parts[2].lstrip()
    return metadata, text


def first_heading(body: str) -> str:
    for line in body.splitlines():
        if line.startswith("#"):
            return line.lstrip("#").strip()
    return ""


def first_use_line(body: str) -> str:
    for line in body.splitlines():
        lowered = line.lower()
        if lowered.startswith("use ") or "use this skill" in lowered or "use when" in lowered:
            return line.strip()
    return ""


def discover_skills(root: Path) -> list[dict[str, Any]]:
    skills_dir = root / "skills"
    results: list[dict[str, Any]] = []
    if not skills_dir.exists():
        return results

    for skill_file in sorted(skills_dir.glob("*/SKILL.md")):
        rel = skill_file.relative_to(root)
        text = skill_file.read_text(encoding="utf-8", errors="replace")
        metadata, body = strip_frontmatter(text)
        name = normalize_skill_name(metadata.get("name") or skill_file.parent.name)
        heading = first_heading(body)
        trigger = metadata.get("description") or first_use_line(body)
        searchable = " ".join([name, heading, trigger, body[:1000]]).lower()
        governance_flags = sorted({keyword for keyword in GOVERNANCE_KEYWORDS if keyword in searchable})
        if name in KNOWN_GATE_SKILLS:
            governance_flags.append("known-gate-skill")
        results.append(
            {
                "name": name,
                "path": str(rel),
                "heading": heading,
                "description": trigger,
                "governance_flags": sorted(set(governance_flags)),
                "direct_path": str(rel),
            }
        )
    return results


def read_registry(root: Path) -> dict[str, Any] | None:
    for rel in ("skills/registry.json", "skills/INDEX.json", "docs/skills/SKILL_INDEX.json"):
        path = root / rel
        if path.exists():
            try:
                return {"path": rel, "data": json.loads(path.read_text(encoding="utf-8"))}
            except json.JSONDecodeError as exc:
                return {"path": rel, "error": str(exc), "data": None}
    return None


def registry_entries(registry: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not registry or not registry.get("data"):
        return []
    data = registry["data"]
    if isinstance(data, dict) and isinstance(data.get("skills"), list):
        return [entry for entry in data["skills"] if isinstance(entry, dict)]
    if isinstance(data, list):
        return [entry for entry in data if isinstance(entry, dict)]
    return []


def validate_registry(root: Path, inventory: list[dict[str, Any]]) -> dict[str, Any]:
    registry = read_registry(root)
    actual_by_name = {skill["name"]: skill for skill in inventory}
    actual_paths = {skill["path"] for skill in inventory}
    drift: list[dict[str, str]] = []

    for entry in registry_entries(registry):
        name = normalize_skill_name(str(entry.get("name", "")))
        path = str(entry.get("path", ""))
        if name and name not in actual_by_name:
            drift.append({"type": "registry_missing_skill", "name": name, "path": path})
        elif path and path not in actual_paths:
            drift.append({"type": "registry_path_mismatch", "name": name, "path": path})

    registry_names = {normalize_skill_name(str(entry.get("name", ""))) for entry in registry_entries(registry)}
    for name, skill in actual_by_name.items():
        if registry and registry_names and name not in registry_names:
            drift.append({"type": "unregistered_skill", "name": name, "path": skill["path"]})

    return {"registry_path": registry.get("path") if registry else None, "drift": drift}


def direct_skill_lookup(root: Path, skill_name: str) -> dict[str, Any]:
    normalized = normalize_skill_name(skill_name)
    folder = normalized.lstrip("/")
    path = root / "skills" / folder / "SKILL.md"
    return {"requested": normalized, "path": str(path.relative_to(root)), "exists": path.exists()}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="List Local Agent Workshop skills from skills/*/SKILL.md.")
    parser.add_argument("root", nargs="?", default=".", help="Repository root.")
    parser.add_argument("--skill", help="Direct skill name to check first.")
    parser.add_argument("--validate-registry", action="store_true", help="Compare registry/index data with skill tree.")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Emit JSON.")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    inventory = discover_skills(root)
    payload: dict[str, Any] = {
        "root": str(root),
        "sources_checked": ["skills/*/SKILL.md"],
        "skills": inventory,
    }
    if args.skill:
        payload["direct_lookup"] = direct_skill_lookup(root, args.skill)
        payload["sources_checked"].insert(0, payload["direct_lookup"]["path"])
    if args.validate_registry:
        payload["registry_validation"] = validate_registry(root, inventory)
        payload["sources_checked"].extend(
            ["skills/registry.json", "skills/INDEX.md", "docs/skills/SKILL_INDEX.md"]
        )

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
