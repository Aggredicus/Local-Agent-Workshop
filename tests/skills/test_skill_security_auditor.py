from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "skills" / "skill_security_auditor.py"


def test_safe_fixture_reports_pass(tmp_path: Path) -> None:
    fixture = ROOT / "tests" / "fixtures" / "skills" / "skill-security-auditor" / "safe-skill"
    output = tmp_path / "report.json"

    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(fixture), "--json", "--out", str(output), "--run-id", "test-safe"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    report = json.loads(output.read_text())
    assert report["skill"] == "skill-security-auditor"
    assert report["input_summary"]["verdict"] == "pass"
    assert report["findings"] == []


def test_review_needed_fixture_flags_process_shell_mode(tmp_path: Path) -> None:
    candidate = tmp_path / "candidate"
    scripts = candidate / "scripts"
    scripts.mkdir(parents=True)
    (candidate / "SKILL.md").write_text("# Candidate\n")
    risky_text = "import subprocess\nsubprocess.run('echo hi', " + "she" + "ll=True)\n"
    (scripts / "example.py").write_text(risky_text)

    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(candidate), "--json", "--strict", "--run-id", "test-review"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert report["input_summary"]["verdict"] == "fail"
    assert any(f["category"] == "shell" for f in report["findings"])
