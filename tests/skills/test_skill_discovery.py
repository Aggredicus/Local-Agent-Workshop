from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LIST_SCRIPT = ROOT / "scripts" / "skills" / "list_available_skills.py"
SELECT_SCRIPT = ROOT / "scripts" / "skills" / "select_skill.py"
FIXTURE_REPO = ROOT / "tests" / "fixtures" / "skills" / "skill-discovery" / "repo"


def run_json(args: list[str]) -> dict:
    result = subprocess.run(args, check=False, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_direct_path_lookup_finds_merge_review() -> None:
    report = run_json([sys.executable, str(LIST_SCRIPT), str(FIXTURE_REPO), "--skill", "merge-review", "--json"])
    assert report["direct_lookup"]["requested"] == "/merge-review"
    assert report["direct_lookup"]["exists"] is True
    assert report["direct_lookup"]["path"] == "skills/merge-review/SKILL.md"


def test_broad_search_failure_is_not_treated_as_absence_when_direct_skill_named() -> None:
    report = run_json(
        [
            sys.executable,
            str(SELECT_SCRIPT),
            str(FIXTURE_REPO),
            "--task",
            "unrelated wording that does not mention merge or review",
            "--skill",
            "merge-review",
            "--json",
        ]
    )
    assert report["direct_lookup"]["exists"] is True
    assert report["selected_primary_skill"]["name"] == "/merge-review"


def test_registry_drift_is_detected() -> None:
    report = run_json([sys.executable, str(LIST_SCRIPT), str(FIXTURE_REPO), "--validate-registry", "--json"])
    drift_types = {item["type"] for item in report["registry_validation"]["drift"]}
    assert "registry_missing_skill" in drift_types
    assert "unregistered_skill" in drift_types


def test_merge_task_ranks_merge_review() -> None:
    report = run_json(
        [
            sys.executable,
            str(SELECT_SCRIPT),
            str(FIXTURE_REPO),
            "--task",
            "Please do the final review and merge this pull request",
            "--json",
        ]
    )
    assert report["selected_primary_skill"]["name"] == "/merge-review"
    assert "merge-review/SKILL.md" in report["selected_primary_skill"]["path"]


def test_external_skill_import_ranks_skill_security_auditor() -> None:
    report = run_json(
        [
            sys.executable,
            str(SELECT_SCRIPT),
            str(FIXTURE_REPO),
            "--task",
            "Import and activate an upstream external skill with scripts",
            "--json",
        ]
    )
    assert report["selected_primary_skill"]["name"] == "/skill-security-auditor"


def test_new_skill_proposal_checks_existing_overlap_before_recommending_creation() -> None:
    report = run_json(
        [
            sys.executable,
            str(SELECT_SCRIPT),
            str(FIXTURE_REPO),
            "--task",
            "Create a new skill for dependency manifest review and package license checks",
            "--json",
        ]
    )
    assert report["new_skill_needed"] is False
    assert report["selected_primary_skill"]["name"] == "/dependency-auditor"
