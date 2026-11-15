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


def test_unsupported_windows_payload_is_explicitly_unreviewed(tmp_path: Path):
    (tmp_path / 'SKILL.md').write_text('# Candidate\n')
    (tmp_path / 'launch.ps1').write_text('Invoke-Expression $input\n')
    result = subprocess.run([sys.executable, str(SCRIPT), str(tmp_path), '--json', '--strict'], capture_output=True, text=True)
    report = json.loads(result.stdout)
    assert result.returncode == 1
    assert report['input_summary']['verdict'] == 'review'
    assert report['evidence']['unreviewed_files'] == [{'path': 'launch.ps1', 'reason': 'unsupported file type'}]


def test_oversized_file_cannot_produce_complete_pass(tmp_path: Path):
    (tmp_path / 'SKILL.md').write_text('# Candidate\n')
    (tmp_path / 'large.py').write_text('#' * 1_000_001)
    result = subprocess.run([sys.executable, str(SCRIPT), str(tmp_path), '--json', '--strict'], capture_output=True, text=True)
    report = json.loads(result.stdout)
    assert result.returncode == 1
    assert report['input_summary']['coverage_complete'] is False
    assert report['evidence']['unreviewed_files'][0]['reason'] == 'size limit'


def test_unreadable_directory_is_not_reported_as_complete_coverage(tmp_path: Path):
    import os
    import pytest
    if os.name == 'nt' or (hasattr(os, 'geteuid') and os.geteuid() == 0):
        pytest.skip('POSIX unprivileged directory permission test')
    (tmp_path / 'SKILL.md').write_text('# Candidate\n')
    hidden = tmp_path / 'unreadable'
    hidden.mkdir()
    (hidden / 'danger.py').write_text('eval(untrusted)\n')
    hidden.chmod(0)
    try:
        result = subprocess.run([sys.executable, str(SCRIPT), str(tmp_path), '--json', '--strict'], capture_output=True, text=True)
    finally:
        hidden.chmod(0o700)
    report = json.loads(result.stdout)
    assert result.returncode == 1
    assert report['input_summary']['coverage_complete'] is False
    assert {'path': 'unreadable', 'reason': 'unreadable directory'} in report['evidence']['unreviewed_files']
