import json
import subprocess
from pathlib import Path

import pytest

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


def test_quiet_keeps_blockers_warnings_and_failure_status(monkeypatch, capsys):
    monkeypatch.setattr(repo_cleanup, 'collect_findings', lambda phase: [
        repo_cleanup.Finding('INFO', 'routine detail'),
        repo_cleanup.Finding('WARN', 'review needed'),
        repo_cleanup.Finding('BLOCKER', 'broken state'),
    ])
    assert repo_cleanup.main(['--quiet']) == 1
    out = capsys.readouterr().out
    assert 'routine detail' not in out
    assert 'review needed' in out and 'broken state' in out
    assert '1 blockers, 1 warnings, 1 info' in out


@pytest.mark.parametrize('content', [b'[{}]', b'{"cards":42}', b'\xff'])
def test_cleanup_reports_invalid_state_instead_of_reparsing_and_crashing(tmp_path, monkeypatch, content):
    state = tmp_path / 'state.json'
    packet = tmp_path / 'packet.txt'
    state.write_bytes(content)
    packet.write_text('derived packet')
    (tmp_path / 'scripts').mkdir()
    (tmp_path / 'scripts/validate_hyperkanban.py').write_text('')
    monkeypatch.setattr(repo_cleanup, 'ROOT', tmp_path)
    monkeypatch.setattr(repo_cleanup, 'run', lambda command: subprocess.CompletedProcess(command, 1, 'invalid state', ''))
    monkeypatch.setattr(repo_cleanup, 'HYPERKANBAN_STATE', state)
    monkeypatch.setattr(repo_cleanup, 'HYPERKANBAN_PACKET', packet)
    findings = []
    repo_cleanup.check_hyperkanban(findings)
    assert any(f.severity == 'BLOCKER' for f in findings)


def test_cleanup_reuses_validated_snapshot_for_blocked_reason_warning(tmp_path, monkeypatch):
    from workshop.hyperkanban.state import build_packet
    data = json.loads(Path('orchestration/hyperkanban/state.json').read_text())
    data['cards'][0]['coords']['state'] = 'blocked'
    data['cards'][0]['byte'] = 4
    data['cards'][0].pop('blocked_reason', None)
    state = tmp_path / 'state.json'
    packet = tmp_path / 'packet.txt'
    state.write_text(json.dumps(data))
    packet.write_text(build_packet(data))
    (tmp_path / 'scripts').mkdir()
    (tmp_path / 'scripts/validate_hyperkanban.py').write_text('')
    monkeypatch.setattr(repo_cleanup, 'ROOT', tmp_path)
    monkeypatch.setattr(repo_cleanup, 'run', lambda command: subprocess.CompletedProcess(command, 0, 'valid state', ''))
    monkeypatch.setattr(repo_cleanup, 'HYPERKANBAN_STATE', state)
    monkeypatch.setattr(repo_cleanup, 'HYPERKANBAN_PACKET', packet)
    findings = []
    repo_cleanup.check_hyperkanban(findings)
    assert not any(f.severity == 'BLOCKER' for f in findings)
    assert any('blocked_reason' in f.message for f in findings)
