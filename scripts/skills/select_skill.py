#!/usr/bin/env python3
"""
Select the most relevant Local Agent Workshop skill for a task.

Read-only helper for /skill-discovery.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from list_available_skills import MANDATORY_SKILL_RULES, discover_skills, direct_skill_lookup, validate_registry  # noqa: E402


MANDATORY_RULES = [{'skill': '/' + name, 'terms': terms, 'reason': reason}
                   for name, terms, reason in MANDATORY_SKILL_RULES]


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def skill_text(skill: dict[str, Any]) -> str:
    return normalize(
        " ".join(
            [
                str(skill.get("name", "")),
                str(skill.get("heading", "")),
                str(skill.get("description", "")),
                " ".join(skill.get("governance_flags", [])),
            ]
        )
    )


def term_score(task: str, candidate_text: str) -> int:
    score = 0
    for token in re.findall(r"[a-zA-Z0-9_.*/-]+", task.lower()):
        if len(token) < 4:
            continue
        if token in candidate_text:
            score += 1
    return score


def select_skills(root: Path, task: str, named_skill: str | None = None) -> dict[str, Any]:
    task_norm = normalize(task)
    inventory = discover_skills(root)
    by_name = {skill["name"]: skill for skill in inventory}

    direct_lookup = direct_skill_lookup(root, named_skill) if named_skill else None
    candidates: dict[str, dict[str, Any]] = {}

    def add_candidate(name: str, reason: str, base_score: int) -> None:
        skill = by_name.get(name)
        if not skill:
            return
        existing = candidates.setdefault(name, {"skill": skill, "score": 0, "reasons": []})
        existing["score"] += base_score
        existing["reasons"].append(reason)

    if named_skill:
        normalized = named_skill if named_skill.startswith("/") else f"/{named_skill}"
        add_candidate(normalized, "User named this skill; direct path was checked before broad matching.", 100)

    for rule in MANDATORY_RULES:
        if any(term in task_norm for term in rule["terms"]):
            add_candidate(rule["skill"], rule["reason"], 80)

    for skill in inventory:
        text = skill_text(skill)
        score = term_score(task_norm, text)
        if score:
            add_candidate(skill["name"], "Task terms overlap this skill's name, description, heading, or flags.", score)

    ranked = sorted(candidates.values(), key=lambda item: (-item["score"], item["skill"]["name"]))
    selected = ranked[0] if ranked else None
    alternatives = []
    for item in ranked[1:]:
        alternatives.append(
            {
                "name": item["skill"]["name"],
                "path": item["skill"]["path"],
                "score": item["score"],
                "reasons": item["reasons"],
            }
        )

    registry_validation = validate_registry(root, inventory)

    return {
        "skill": "skill-discovery",
        "mode": "analysis",
        "task_summary": task,
        "branch_or_ref_checked": "local-working-tree-or-provided-root",
        "skill_sources_checked": [
            "skills/*/SKILL.md",
            "skills/registry.json if present",
            "skills/INDEX.json if present",
            "docs/skills/SKILL_INDEX.json if present",
            "direct skill path when named",
        ],
        "direct_lookup": direct_lookup,
        "selected_primary_skill": None
        if not selected
        else {
            "name": selected["skill"]["name"],
            "path": selected["skill"]["path"],
            "score": selected["score"],
            "reasons": selected["reasons"],
        },
        "secondary_or_composed_skills": alternatives,
        "alternatives_considered": [
            {"name": skill["name"], "path": skill["path"]}
            for skill in inventory
            if not selected or skill["name"] != selected["skill"]["name"]
        ],
        "evidence_paths": [skill["path"] for skill in inventory],
        "registry_tree_drift": registry_validation["drift"],
        "new_skill_needed": selected is None,
        "approval_boundary": "Human approval required for merge policy, governance changes, or bypassing selected gate skills.",
        "recommended_next_action": "Read the selected skill's SKILL.md and follow its workflow."
        if selected
        else "Create or improve a skill only after confirming no overlap exists.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Select an applicable Local Agent Workshop skill for a task.")
    parser.add_argument("root", nargs="?", default=".", help="Repository root.")
    parser.add_argument("--task", required=True, help="Task summary.")
    parser.add_argument("--skill", help="Named skill to check directly before ranking.")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Emit JSON.")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    try:
        report = select_skills(root, args.task, args.skill)
    except (OSError, ValueError):
        print(json.dumps({'error': 'Skill discovery failed; inspect library validation and permissions.', 'new_skill_needed': False}))
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
