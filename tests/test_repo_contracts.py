"""Malformed registries fail as reports, never tracebacks or false passes."""
from __future__ import annotations

import json
import pytest

import validate_repo_contracts as contracts


@pytest.fixture
def registry(tmp_path):
    (tmp_path / 'schemas').mkdir()
    (tmp_path / 'schemas/demo.json').write_text('{}')
    return {
        'schema_version': '0.1.0', 'artifact_type': 'schema_registry', 'generated_by': 'test',
        'schemas': [{
            'schema_id': 'demo', 'name': 'Demo', 'version': '0.1.0',
            'path': 'schemas/demo.json', 'owner_protocol': 'docs/demo.md', 'status': 'draft',
            'compatible_versions': [], 'example_paths': [],
            'validation_command': 'not executed', 'migration_notes': 'Initial draft.',
        }],
    }


def run_registry(tmp_path, data, capsys, *args):
    path = tmp_path / 'registry.json'
    path.write_text(json.dumps(data))
    code = contracts.main(['--root', str(tmp_path), '--schema-registry', 'registry.json', '--format', 'json', *args])
    return code, json.loads(capsys.readouterr().out)


@pytest.mark.parametrize('value', [None, [], 'registry', 1, True])
def test_invalid_registry_roots_fail_as_json(tmp_path, capsys, value):
    code, report = run_registry(tmp_path, value, capsys)
    assert code == 1
    assert report['summary']['errors'] > 0


@pytest.mark.parametrize('value', [[], {}, None, 123])
def test_invalid_status_types_are_errors(tmp_path, registry, capsys, value):
    registry['schemas'][0]['status'] = value
    code, report = run_registry(tmp_path, registry, capsys)
    assert code == 1 and report['summary']['errors']


@pytest.mark.parametrize('field,value', [
    ('name', None), ('name', ''), ('owner_protocol', []), ('validation_command', False),
    ('compatible_versions', '0.1.x'), ('compatible_versions', [{}]),
    ('compatible_versions', ['0.1.x', '0.1.x']), ('example_paths', [None]),
])
def test_malformed_record_fields_are_errors(tmp_path, registry, capsys, field, value):
    registry['schemas'][0][field] = value
    code, report = run_registry(tmp_path, registry, capsys)
    assert code == 1 and report['summary']['errors']


@pytest.mark.parametrize('path', ['../outside.json', '/tmp/outside.json', 'C:\\outside.json', 'C:outside.json', '\\\\server\\share\\schema.json', 'bad\x00path'])
def test_registry_paths_cannot_escape_repository(tmp_path, registry, capsys, path):
    registry['schemas'][0]['path'] = path
    registry['schemas'][0]['status'] = 'planned'
    code, report = run_registry(tmp_path, registry, capsys)
    assert code == 1 and report['summary']['errors']


def test_directory_is_not_a_schema(tmp_path, registry, capsys):
    registry['schemas'][0]['path'] = 'schemas'
    code, report = run_registry(tmp_path, registry, capsys)
    assert code == 1 and report['summary']['errors']


def test_symlink_cannot_escape_repository(tmp_path, registry, capsys):
    outside = tmp_path.parent / (tmp_path.name + '-outside.json')
    outside.write_text('{}')
    (tmp_path / 'schemas/escape.json').symlink_to(outside)
    registry['schemas'][0]['path'] = 'schemas/escape.json'
    code, report = run_registry(tmp_path, registry, capsys)
    assert code == 1 and report['summary']['errors']


def test_external_registry_argument_returns_json_without_reading_it(tmp_path, capsys, monkeypatch):
    outside = tmp_path.parent / (tmp_path.name + '-private.json')
    outside.write_text('PRIVATE_CANARY_DO_NOT_READ')
    monkeypatch.setattr(contracts, 'load_json', lambda path: pytest.fail('External registry was opened'))
    code = contracts.main(['--root', str(tmp_path), '--schema-registry', str(outside), '--format', 'json'])
    out = capsys.readouterr().out
    assert code == 1 and 'PRIVATE_CANARY_DO_NOT_READ' not in out
    assert json.loads(out)['summary']['errors']


@pytest.mark.parametrize('kind', ['invalid_utf8', 'directory'])
def test_unreadable_registry_returns_structured_error(tmp_path, capsys, kind):
    p = tmp_path / 'registry.json'
    if kind == 'invalid_utf8':
        p.write_bytes(b'\xff')
    else:
        p.mkdir()
    code = contracts.main(['--root', str(tmp_path), '--schema-registry', p.name, '--format', 'json'])
    assert code == 1
    assert json.loads(capsys.readouterr().out)['summary']['errors']


def test_valid_draft_registry_passes(tmp_path, registry, capsys):
    code, report = run_registry(tmp_path, registry, capsys)
    assert code == 0 and report['summary']['errors'] == 0


def test_example_path_cannot_escape_repository(tmp_path, registry, capsys):
    registry['schemas'][0]['example_paths'] = ['../private.json']
    code, report = run_registry(tmp_path, registry, capsys)
    assert code == 1 and report['summary']['errors']


@pytest.mark.parametrize('field', ['schema_id', 'version'])
def test_metadata_identifiers_cannot_have_trailing_newlines(tmp_path, registry, capsys, field):
    registry['schemas'][0][field] += '\n'
    code, report = run_registry(tmp_path, registry, capsys)
    assert code == 1 and report['summary']['errors']


def test_planned_paths_and_quiet_reports_keep_honest_counts(tmp_path, registry, capsys):
    registry['schemas'][0].update(status='planned', path='schemas/future.json')
    code, report = run_registry(tmp_path, registry, capsys)
    assert code == 0 and report['summary']['info'] == 1
    report['findings'].extend([
        {'severity': 'ERROR', 'category': 'test', 'message': 'broken contract', 'hint': 'fix it'},
        {'severity': 'WARN', 'category': 'test', 'message': 'review contract', 'hint': ''},
    ])
    report['summary'] = contracts.summarize([contracts.Finding(**f) for f in report['findings']])
    text = contracts.render_text(report, quiet=True)
    assert 'planned path' not in text
    assert 'broken contract' in text and 'review contract' in text and 'fix it' in text
    assert '1 errors, 1 warnings, 1 info' in text
