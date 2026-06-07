from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "skills" / "dependency_auditor.py"
FIXTURES = ROOT / "tests" / "fixtures" / "skills" / "dependency-auditor"


def test_clean_project_reports_pass(tmp_path: Path) -> None:
    output = tmp_path / "report.json"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(FIXTURES / "clean-project"), "--json", "--out", str(output), "--run-id", "test-clean"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    report = json.loads(output.read_text())
    assert report["skill"] == "dependency-auditor"
    assert report["input_summary"]["verdict"] == "pass"
    assert report["input_summary"]["dependency_count"] == 2
    assert report["findings"] == []


def test_review_project_flags_broad_versions_and_missing_license() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(FIXTURES / "review-project"), "--json", "--strict", "--run-id", "test-review"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert report["input_summary"]["verdict"] == "fail"
    categories = {finding["category"] for finding in report["findings"]}
    assert "license" in categories
    assert "version" in categories
    assert "source" in categories
    assert any(finding["severity"] == "high" for finding in report["findings"])
