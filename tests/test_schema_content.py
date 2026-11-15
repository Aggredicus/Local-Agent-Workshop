"""Maintained schema evaluation stays offline and omits example values."""
import builtins
import json
import urllib.request

import pytest

import validate_repo_contracts as contracts


@pytest.fixture
def project(tmp_path):
    (tmp_path / 'schemas').mkdir()
    (tmp_path / 'examples').mkdir()
    schema = {'$schema': 'https://json-schema.org/draft/2020-12/schema', 'type': 'object',
              'required': ['count'], 'properties': {'count': {'type': 'integer'}}, 'additionalProperties': False}
    (tmp_path / 'schemas/demo.json').write_text(json.dumps(schema))
    (tmp_path / 'examples/demo.json').write_text('{"count":1}')
    registry = {'schema_version': '0.1.0', 'artifact_type': 'schema_registry', 'generated_by': 'test', 'schemas': [{
        'schema_id': 'demo', 'name': 'Demo', 'version': '0.1.0', 'path': 'schemas/demo.json',
        'owner_protocol': 'test', 'status': 'active', 'compatible_versions': [],
        'example_paths': ['examples/demo.json'], 'validation_command': 'NOT EXECUTED', 'migration_notes': 'Initial',
    }]}
    (tmp_path / 'registry.json').write_text(json.dumps(registry))
    return tmp_path


def run(project, capsys, *, schemas=True):
    args = ['--root', str(project), '--schema-registry', 'registry.json', '--format', 'json']
    if schemas:
        args.append('--schemas')
    code = contracts.main(args)
    raw = capsys.readouterr().out
    return code, json.loads(raw), raw


def test_valid_schema_and_example_are_checked(project, capsys):
    code, report, _ = run(project, capsys)
    assert code == 0
    assert report['schema_content']['schemas_checked'] == 1
    assert report['schema_content']['examples_checked'] == 1
    assert report['schema_content']['network_retrieval'] is False


def test_invalid_schema_is_not_an_exist_only_pass(project, capsys):
    (project / 'schemas/demo.json').write_text('{"type":42}')
    code, report, _ = run(project, capsys)
    assert code == 1 and report['summary']['errors']


def test_example_error_never_serializes_private_values(project, capsys):
    (project / 'examples/demo.json').write_text('{"count":"PRIVATE_SCHEMA_CANARY"}')
    code, report, raw = run(project, capsys)
    assert code == 1 and report['summary']['errors']
    assert 'PRIVATE_SCHEMA_CANARY' not in raw


def test_remote_reference_never_uses_network_even_without_examples(project, capsys, monkeypatch):
    (project / 'schemas/demo.json').write_text('{"$ref":"https://example.invalid/private-schema.json"}')
    p = project / 'registry.json'
    registry = json.loads(p.read_text())
    registry['schemas'][0].update(status='draft', example_paths=[])
    p.write_text(json.dumps(registry))
    monkeypatch.setattr(urllib.request, 'urlopen', lambda *a, **k: pytest.fail('Network retrieval attempted'))
    code, report, _ = run(project, capsys)
    assert code == 1 and report['schema_content']['references_checked'] == 1


@pytest.mark.parametrize('reference', ['value.json', 'https://law.invalid/value'])
def test_preloaded_forward_references_work_offline(project, capsys, reference):
    (project / 'schemas/demo.json').write_text(json.dumps({'$ref': reference}))
    (project / 'schemas/value.json').write_text('{"$id":"https://law.invalid/value","type":"integer"}')
    (project / 'examples/demo.json').write_text('12')
    p = project / 'registry.json'
    registry = json.loads(p.read_text())
    target = registry['schemas'][0].copy()
    target.update(schema_id='value', path='schemas/value.json', status='draft', example_paths=[])
    registry['schemas'].append(target)
    p.write_text(json.dumps(registry))
    code, report, _ = run(project, capsys)
    assert code == 0 and report['schema_content']['schemas_checked'] == 2


def test_missing_development_tools_fail_explicitly_but_metadata_stays_standalone(project, capsys, monkeypatch):
    original = builtins.__import__
    def deny(name, *args, **kwargs):
        if name in {'jsonschema', 'referencing'}:
            raise ImportError('Synthetic missing development tool')
        return original(name, *args, **kwargs)
    monkeypatch.setattr(builtins, '__import__', deny)
    code, report, _ = run(project, capsys)
    assert code == 1 and not report['schema_content']['available']
    code, report, _ = run(project, capsys, schemas=False)
    assert code == 0 and 'schema_content' not in report


def test_registry_parser_reports_excessive_nesting(project, capsys):
    (project / 'registry.json').write_text('[' * 3000 + '0' + ']' * 3000)
    code, report, _ = run(project, capsys)
    assert code == 1 and report['summary']['errors']


def test_unknown_schema_dialect_is_an_error(project, capsys):
    (project / 'schemas/demo.json').write_text('{"$schema":"https://example.invalid/custom-dialect"}')
    code, report, _ = run(project, capsys)
    assert code == 1 and report['summary']['errors']


def test_reference_like_annotation_data_is_not_mistaken_for_schema(project, capsys):
    path = project / 'schemas/demo.json'
    schema = json.loads(path.read_text())
    schema['examples'] = [{'$ref': 'https://example.invalid/this-is-data'}]
    path.write_text(json.dumps(schema))
    code, report, _ = run(project, capsys)
    assert code == 0 and report['schema_content']['references_checked'] == 0


def test_duplicate_schema_ids_fail(project, capsys):
    path = project / 'schemas/demo.json'
    schema = json.loads(path.read_text())
    schema['$id'] = 'https://law.invalid/duplicate'
    path.write_text(json.dumps(schema))
    (project / 'schemas/duplicate.json').write_text(json.dumps(schema))
    p = project / 'registry.json'
    registry = json.loads(p.read_text())
    duplicate = registry['schemas'][0].copy()
    duplicate.update(schema_id='duplicate', path='schemas/duplicate.json', status='draft', example_paths=[])
    registry['schemas'].append(duplicate)
    p.write_text(json.dumps(registry))
    code, report, _ = run(project, capsys)
    assert code == 1 and report['summary']['errors']


def test_cyclic_schema_evaluation_returns_error_instead_of_traceback(project, capsys):
    (project / 'schemas/demo.json').write_text('{"$ref":"#"}')
    code, report, _ = run(project, capsys)
    assert code == 1 and report['summary']['errors']
