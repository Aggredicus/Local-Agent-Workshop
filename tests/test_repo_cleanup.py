import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import repo_cleanup


def test_finding_renders_with_category_and_hint():
    finding = repo_cleanup.Finding("WARN", "example warning", "fix it", category="tests")
    rendered = finding.render()
    assert "[WARN] tests: example warning" in rendered
    assert "hint: fix it" in rendered


def test_finding_to_dict_includes_category():
    finding = repo_cleanup.Finding("INFO", "hello", category="run")
    assert finding.to_dict() == {
        "severity": "INFO",
        "message": "hello",
        "hint": "",
        "category": "run",
    }


def test_summarize_counts_findings():
    findings = [
        repo_cleanup.Finding("INFO", "a"),
        repo_cleanup.Finding("WARN", "b"),
        repo_cleanup.Finding("BLOCKER", "c"),
        repo_cleanup.Finding("INFO", "d"),
    ]
    assert repo_cleanup.summarize(findings) == {
        "blockers": 1,
        "warnings": 1,
        "info": 2,
        "total": 4,
    }


def test_build_report_is_json_serializable():
    findings = [repo_cleanup.Finding("INFO", "cleanup phase: before", category="run")]
    report = repo_cleanup.build_report("before", findings)
    encoded = json.dumps(report)
    decoded = json.loads(encoded)
    assert decoded["phase"] == "before"
    assert decoded["summary"]["info"] == 1
    assert decoded["findings"][0]["category"] == "run"


def test_render_text_includes_summary():
    report = repo_cleanup.build_report(
        "after",
        [
            repo_cleanup.Finding("INFO", "cleanup phase: after", category="run"),
            repo_cleanup.Finding("WARN", "sample warning", category="docs"),
        ],
    )
    rendered = repo_cleanup.render_text(report)
    assert "Repository cleanup audit" in rendered
    assert "[WARN] docs: sample warning" in rendered
    assert "summary: 0 blockers, 1 warnings, 1 info" in rendered


def test_write_output_writes_file(tmp_path, capsys):
    out = tmp_path / "cleanup" / "latest.json"
    repo_cleanup.write_output('{"ok": true}\n', out)
    assert out.read_text(encoding="utf-8") == '{"ok": true}\n'
    captured = capsys.readouterr()
    assert "wrote cleanup report" in captured.out


def test_main_json_output_to_file(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(
        repo_cleanup,
        "collect_findings",
        lambda phase: [repo_cleanup.Finding("INFO", f"cleanup phase: {phase}", category="run")],
    )
    out = tmp_path / "latest.json"
    assert repo_cleanup.main(["--phase", "before", "--format", "json", "--out", str(out)]) == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["phase"] == "before"
    assert payload["summary"]["blockers"] == 0
    assert payload["findings"][0]["category"] == "run"
    captured = capsys.readouterr()
    assert "wrote cleanup report" in captured.out


def test_main_returns_failure_when_blockers_exist(monkeypatch):
    monkeypatch.setattr(
        repo_cleanup,
        "collect_findings",
        lambda phase: [repo_cleanup.Finding("BLOCKER", "broken", category="tests")],
    )
    assert repo_cleanup.main(["--phase", "after", "--format", "json"]) == 1
