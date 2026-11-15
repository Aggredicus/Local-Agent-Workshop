"""Discovery must not read linked secrets or block on non-regular skill files."""
from pathlib import Path
import os
import json
import subprocess
import sys

import pytest

from workshop import cli
from workshop.doctor import run_doctor
from workshop.skills import discover_skills, inspect_skill


@pytest.mark.parametrize('kind', ['file-link', 'directory-link', 'root-link', 'invalid-utf8', 'directory', 'fifo'])
def test_discovery_reports_unsafe_documents_without_reading_them(tmp_path, monkeypatch, kind):
    root = tmp_path / 'skills'
    private = tmp_path / 'private/demo'
    private.mkdir(parents=True)
    (private / 'SKILL.md').write_text('---\nname: demo\ndescription: PRIVATE_DESCRIPTION_CANARY\n---\n')
    if kind == 'root-link':
        root.symlink_to(private.parent, target_is_directory=True)
    else:
        root.mkdir()
        target = root / 'demo'
        if kind == 'directory-link':
            target.symlink_to(private, target_is_directory=True)
        else:
            target.mkdir()
            doc = target / 'SKILL.md'
            if kind == 'file-link':
                doc.symlink_to(private / 'SKILL.md')
            elif kind == 'invalid-utf8':
                doc.write_bytes(b'\xff')
            elif kind == 'directory':
                doc.mkdir()
            else:
                os.mkfifo(doc)
    original = Path.read_text
    def reject_unsafe_read(path, *args, **kwargs):
        if path.name == 'SKILL.md' and kind in {'file-link', 'directory-link', 'root-link', 'fifo'}:
            pytest.fail('Discovery tried reading an unsafe skill document')
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, 'read_text', reject_unsafe_read)
    skills = discover_skills(root)
    assert skills and all(s.errors for s in skills)
    assert all('PRIVATE_DESCRIPTION_CANARY' not in s.description for s in skills)


def test_unreadable_document_is_structured_error(tmp_path, monkeypatch):
    doc = tmp_path / 'demo/SKILL.md'
    doc.parent.mkdir()
    doc.write_text('not read')
    original = Path.read_text
    def deny(path, *args, **kwargs):
        if path == doc:
            raise PermissionError('synthetic read failure')
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, 'read_text', deny)
    assert inspect_skill(doc).errors


def test_doctor_and_cli_report_corrupt_skill_without_traceback(tmp_path, capsys):
    doc = tmp_path / 'skills/demo/SKILL.md'
    doc.parent.mkdir(parents=True)
    doc.write_bytes(b'\xff')
    checks = run_doctor(tmp_path)
    assert any(c.name == 'skills' and c.level == 'FAIL' for c in checks)
    assert cli.main(['skills', '--root', str(doc.parent.parent), 'validate']) == 1
    assert 'INVALID' in capsys.readouterr().err


def test_failed_discovery_does_not_recommend_creating_a_new_skill(tmp_path, capsys):
    doc = tmp_path / 'skills/demo/SKILL.md'
    doc.parent.mkdir(parents=True)
    doc.write_bytes(b'\xff')
    assert cli.main(['skills', '--root', str(doc.parent.parent), 'select', '--task', 'review a project', '--json']) == 1
    report = json.loads(capsys.readouterr().out)
    assert report['discovery_errors'] and not report['new_skill_needed']


@pytest.mark.parametrize('script', ['list_available_skills.py', 'select_skill.py'])
@pytest.mark.parametrize('kind', ['file-link', 'registry-link', 'fifo'])
def test_legacy_helpers_share_read_safety_and_never_print_linked_data(tmp_path, script, kind):
    doc = tmp_path / 'skills/demo/SKILL.md'
    doc.parent.mkdir(parents=True)
    valid = '---\nname: demo\ndescription: Safe demonstration skill\n---\n'
    private = tmp_path / 'private'
    private.write_text('---\nname: demo\ndescription: PRIVATE_LEGACY_CANARY\n---\n')
    if kind == 'file-link':
        doc.symlink_to(private)
    elif kind == 'fifo':
        os.mkfifo(doc)
    else:
        doc.write_text(valid)
        private.write_text('{"skills":[{"name":"PRIVATE_LEGACY_CANARY","path":"private"}]}')
        (tmp_path / 'skills/registry.json').symlink_to(private)
    path = Path(__file__).resolve().parents[1] / 'scripts/skills' / script
    args = [sys.executable, str(path), str(tmp_path), '--json']
    args += ['--task', 'Find a demonstration skill'] if script.startswith('select') else ['--validate-registry']
    result = subprocess.run(args, text=True, capture_output=True, timeout=3)
    assert result.returncode == 1
    assert 'PRIVATE_LEGACY_CANARY' not in result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report['error'] and not report['new_skill_needed']
