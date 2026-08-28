"""Local repository readiness checks for Local Agent Workshop."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import sys

from workshop.hyperkanban.state import HyperKanbanError, load_state
from workshop.skills import discover_skills, validate_skills


@dataclass(frozen=True)
class Check:
    level: str
    name: str
    message: str


def run_doctor(repo_root: Path) -> list[Check]:
    repo_root = repo_root.resolve()
    checks: list[Check] = []

    py_ok = sys.version_info >= (3, 11)
    checks.append(Check("PASS" if py_ok else "FAIL", "python", f"Python {sys.version.split()[0]} (requires >=3.11)"))

    git = shutil.which("git")
    checks.append(Check("PASS" if git else "FAIL", "git", git or "git executable not found"))

    required = ["me.md", "AGENTS.md", "pyproject.toml", "scripts/verify.sh"]
    missing = [name for name in required if not (repo_root / name).exists()]
    checks.append(
        Check("PASS" if not missing else "FAIL", "repo", "core repository files present" if not missing else f"missing: {', '.join(missing)}")
    )

    skills_root = repo_root / "skills"
    skills = discover_skills(skills_root)
    invalid = validate_skills(skills_root)
    legacy = [skill for skill in skills if skill.legacy]
    if not skills:
        checks.append(Check("FAIL", "skills", "no canonical skills found under skills/*/SKILL.md"))
    elif invalid:
        checks.append(Check("FAIL", "skills", f"{len(invalid)} of {len(skills)} skills fail Agent Skills validation"))
    else:
        message = f"{len(skills)} canonical skills are sync-compatible"
        if legacy:
            message += f" ({len(legacy)} legacy skill(s) normalized during sync)"
        checks.append(Check("PASS", "skills", message))

    discoverable = repo_root / ".agents" / "skills"
    synced = discover_skills(discoverable)
    if skills and len(synced) == len(skills):
        checks.append(Check("PASS", "skill-discovery", f"{len(synced)} skills available under .agents/skills"))
    else:
        checks.append(
            Check(
                "WARN",
                "skill-discovery",
                "project skill cache is not synchronized; run `workshop skills sync`",
            )
        )

    state_path = repo_root / "orchestration" / "hyperkanban" / "state.json"
    try:
        load_state(state_path)
    except HyperKanbanError as exc:
        checks.append(Check("FAIL", "hyperkanban", str(exc)))
    else:
        checks.append(Check("PASS", "hyperkanban", "state.json validates"))

    return checks


def format_checks(checks: list[Check]) -> str:
    return "\n".join(f"[{check.level:<4}] {check.name}: {check.message}" for check in checks)


def has_failures(checks: list[Check]) -> bool:
    return any(check.level == "FAIL" for check in checks)
