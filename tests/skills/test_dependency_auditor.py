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


def test_inline_toml_and_optional_build_dependencies_are_counted(tmp_path: Path):
    (tmp_path / 'pyproject.toml').write_text('''[project]
name="example"
license="MIT"
dependencies=["requests", "httpx>=0.27"]
[project.optional-dependencies]
dev=["pytest==8.3"]
[build-system]
requires=["setuptools>=68"]
''')
    result = subprocess.run([sys.executable, str(SCRIPT), str(tmp_path), '--json', '--strict'], capture_output=True, text=True)
    report = json.loads(result.stdout)
    assert result.returncode == 1  # unpinned requests requires review
    assert {d['name'] for d in report['evidence']['dependencies']} == {'requests', 'httpx', 'pytest', 'setuptools'}


def test_malformed_toml_is_not_an_empty_passing_audit(tmp_path: Path):
    (tmp_path / 'pyproject.toml').write_text('[project\ndependencies=["requests"]')
    result = subprocess.run([sys.executable, str(SCRIPT), str(tmp_path), '--json', '--strict'], capture_output=True, text=True)
    assert result.returncode == 1
    assert json.loads(result.stdout)['input_summary']['verdict'] == 'fail'


def test_invalid_toml_container_types_return_report_instead_of_traceback(tmp_path: Path):
    (tmp_path / 'pyproject.toml').write_text('tool=[]\n[project]\nname="example"\nlicense="MIT"\ndynamic=3\n')
    result = subprocess.run([sys.executable, str(SCRIPT), str(tmp_path), '--json', '--strict'], capture_output=True, text=True)
    assert result.returncode == 1
    assert json.loads(result.stdout)['input_summary']['verdict'] == 'fail'
    assert 'Traceback' not in result.stderr
