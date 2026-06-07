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
