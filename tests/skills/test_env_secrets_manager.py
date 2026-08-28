from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "skills" / "env_secrets_manager.py"
FIXTURES = ROOT / "tests" / "fixtures" / "skills" / "env-secrets-manager"


def test_clean_project_reports_pass_and_redacts_values(tmp_path: Path) -> None:
    output = tmp_path / "report.json"
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(FIXTURES / "clean-project"),
            "--example",
            ".env.example",
            "--env",
            ".env.local",
            "--json",
            "--out",
            str(output),
            "--run-id",
            "test-clean",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    report = json.loads(output.read_text())
    assert report["skill"] == "env-secrets-manager"
    assert report["input_summary"]["verdict"] == "pass"
    entries = report["evidence"]["env_entries"]
    assert entries
    assert all(entry["value_redacted"] in {"<redacted>", "<empty>"} for entry in entries)
    assert "local-placeholder" not in json.dumps(report)


def test_review_project_flags_template_value_and_key_drift() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(FIXTURES / "review-project"),
            "--example",
            ".env.example",
            "--env",
            ".env.local",
            "--json",
            "--strict",
            "--run-id",
            "test-review",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert report["input_summary"]["verdict"] == "fail"
    categories = {finding["category"] for finding in report["findings"]}
    assert "redaction" in categories
    assert "drift" in categories
    assert any(finding["severity"] == "high" for finding in report["findings"])
    assert "1234567890abcdef" not in result.stdout


def test_explicit_paths_outside_root_do_not_crash_or_leak_values(tmp_path: Path) -> None:
    project = tmp_path / "project"
    outside = tmp_path / "outside"
    project.mkdir()
    outside.mkdir()
    example = outside / ".env.example"
    env_file = outside / ".env.local"
    example.write_text("TOKEN=CHANGE_ME\nSHARED=value\n", encoding="utf-8")
    env_file.write_text("TOKEN=outside-local-value\nSHARED=runtime\nEXTRA=value\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(project),
            "--example",
            str(example),
            "--env",
            str(env_file),
            "--json",
            "--strict",
            "--run-id",
            "test-outside-paths",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert report["input_summary"]["verdict"] == "review"
    assert any(finding["category"] == "drift" for finding in report["findings"])
    assert "outside-local-value" not in result.stdout
