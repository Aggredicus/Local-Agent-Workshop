#!/usr/bin/env python3
"""Read-only review probes for HEAD's existing modules, using disposable fixtures.

These assertions CONFIRM defects; a successful probe run is not a product test pass.
No application, governance, state, or credential file in the checkout is modified.
"""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from workshop import doctor, skills
from workshop.hyperkanban import state as runtime


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ci = load('review_hk_validator', 'scripts/validate_hyperkanban.py')
dep = load('review_dependencies', 'scripts/skills/dependency_auditor.py')
env = load('review_env', 'scripts/skills/env_secrets_manager.py')
security = load('review_security', 'scripts/skills/skill_security_auditor.py')
contracts = load('review_contracts', 'scripts/validate_repo_contracts.py')
results = []


def record(probe, finding, observed):
    results.append({'probe': probe, 'finding': finding, 'result': 'reproduced', 'observed': observed})


def skill(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('---\nname: demo\ndescription: Demonstration.\n---\n# Demo\n', encoding='utf-8')


with tempfile.TemporaryDirectory(prefix='law-review-') as temporary:
    tmp = Path(temporary)
    base = json.loads((ROOT / 'orchestration/hyperkanban/state.json').read_text())
    altered = copy.deepcopy(base)
    altered['cards'][0]['coords']['ring'] = 'invalid-coordinate'
    runtime.validate_state(altered)
    try:
        ci.validate_coords(ci.validate_card_shape(altered['cards']), ci.validate_axes(altered))
    except ValueError:
        record('validator-disagreement-coordinates', 'R04', 'Runtime accepts a coordinate rejected by the CI validator.')
    else:
        raise AssertionError('Expected CI rejection')

    altered = copy.deepcopy(base)
    altered['cards'][0]['deps'] = [altered['cards'][0]['id']]
    runtime.validate_state(altered)
    try:
        ci.validate_dependencies(ci.validate_card_shape(altered['cards']))
    except ValueError:
        record('validator-disagreement-cycle', 'R04', 'Runtime accepts a self-dependency rejected by CI.')
    else:
        raise AssertionError('Expected cycle rejection')

    altered = copy.deepcopy(base)
    card = altered['cards'][0]
    card['byte'] = runtime.DONE
    card['coords']['state'] = 'done'
    card['test_contract'] = {'required': True}
    card['evidence_paths'] = []
    card['open_exceptions'] = []
    state_path = tmp / 'state.json'
    state_path.write_text(json.dumps(altered))
    ci.validate_state(state_path)
    try:
        runtime.validate_state(altered)
    except runtime.HyperKanbanError:
        record('validator-disagreement-evidence', 'R04', 'CI accepts done-without-evidence; runtime rejects it.')
    else:
        raise AssertionError('Expected evidence rejection')

    altered = copy.deepcopy(base)
    altered['cards'][0]['test_contract'] = {'required': True}
    completed = runtime.complete_card(altered, altered['cards'][0]['id'], evidence=['this/path/does/not/exist'])
    assert runtime.is_done(completed)
    record('nonexistent-completion-evidence', 'R05', 'A nonexistent path satisfies the completion gate.')

    altered = copy.deepcopy(base)
    state_path.write_text(json.dumps(base))
    packet = state_path.with_name('packet.txt')
    packet.write_text(runtime.build_packet(base))
    runtime.complete_card(altered, altered['cards'][0]['id'])
    with patch.object(runtime, 'save_packet', side_effect=OSError('simulated storage failure')):
        try:
            runtime.save_state_and_packet(state_path, altered)
        except OSError:
            pass
    assert json.loads(state_path.read_text()) == altered
    assert packet.read_text() != runtime.build_packet(altered)
    record('partial-state-commit', 'R06', 'An injected packet-write failure leaves state committed and packet stale.')
    packet.unlink()

    source, target = tmp / 'source', tmp / 'target'
    skill(source / 'demo/SKILL.md')
    obsolete = source / 'demo/old-helper.py'
    obsolete.write_text('# inert canary\n')
    skills.sync_skills(source, target)
    obsolete.unlink()
    skills.sync_skills(source, target)
    assert (target / 'demo/old-helper.py').exists()
    record('stale-generated-helper', 'R03', 'A deleted canonical helper remains discoverable after sync.')

    outside, target2 = tmp / 'outside', tmp / 'target2'
    outside.mkdir()
    target2.mkdir()
    (target2 / 'demo').symlink_to(outside, target_is_directory=True)
    skills.sync_skills(source, target2)
    assert (outside / 'SKILL.md').exists()
    record('sync-destination-symlink', 'R02', 'Sync writes to a directory outside the target through a symlink.')

    canary = tmp / 'external-canary.txt'
    canary.write_text('SYNTHETIC DATA ONLY\n')
    (source / 'demo/linked-helper.txt').symlink_to(canary)
    skills.sync_skills(source, target)
    assert (target / 'demo/linked-helper.txt').read_text() == canary.read_text()
    record('sync-source-symlink', 'R02', 'Sync dereferences a source symlink and copies external file contents into the agent cache.')

    repo = tmp / 'doctor-repo'
    for name in ['me.md', 'AGENTS.md', 'pyproject.toml', 'scripts/verify.sh']:
        p = repo / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('example')
    skill(repo / 'skills/demo/SKILL.md')
    skill(repo / '.agents/skills/demo/SKILL.md')
    (repo / '.agents/skills/demo/SKILL.md').write_text('---\nname: wrong\ndescription: Stale\n---\n')
    state_path = repo / 'orchestration/hyperkanban/state.json'
    state_path.parent.mkdir(parents=True)
    state_path.write_text(json.dumps(base))
    checks = doctor.run_doctor(repo)
    assert next(c for c in checks if c.name == 'skill-discovery').level == 'PASS'
    record('doctor-count-only-cache-check', 'R03', 'Doctor reports PASS for an invalid generated skill with the same inventory count.')

    project = tmp / 'project'
    project.mkdir()
    (project / 'pyproject.toml').write_text('[project]\nname="example"\nlicense="MIT"\ndependencies=["requests"]\n')
    report = dep.build_report(project, 'review', [])
    assert report['input_summary']['dependency_count'] == 0 and report['input_summary']['verdict'] == 'pass'
    record('inline-toml-dependencies', 'R07', 'Valid inline pyproject dependencies produce dependency_count=0 and verdict=pass.')

    candidate = tmp / 'candidate'
    candidate.mkdir()
    (candidate / 'SKILL.md').write_text('# Candidate\n')
    (candidate / 'launch.ps1').write_text('Invoke-Expression $untrusted\n')
    report = security.build_report(candidate, 'review', 'analysis', [])
    assert report['input_summary']['verdict'] == 'pass' and report['input_summary']['files_scanned'] == 1
    record('powershell-omitted', 'R08', 'A PowerShell payload is silently excluded; scanner reports pass.')

    # Synthetic marker only. No real credential is read or printed.
    marker = 'SYNTHETIC-CANARY-NOT-A-SECRET'
    (project / '.env').write_text(f'https://operator:{marker}@example.invalid/key=value\n')
    report = env.build_report(project, 'review', [], None, None)
    assert marker in json.dumps(report)
    record('env-report-redaction', 'R01', 'A synthetic credential in a malformed key appears in report JSON.')

    registry = copy.deepcopy(json.loads((ROOT / 'schemas/schema-registry.json').read_text()))
    for item in registry['schemas']:
        if item['schema_id'] == 'schema_registry':
            item['path'] = 'schemas/broken.schema.json'
    fixture_root = tmp / 'contracts'
    (fixture_root / 'schemas').mkdir(parents=True)
    (fixture_root / 'schemas/broken.schema.json').write_text('not JSON at all')
    registry['schemas'] = [registry['schemas'][0]]
    registry['schemas'][0]['example_paths'] = []
    findings = contracts.validate_registry_shape(registry) + contracts.validate_schema_records(registry, fixture_root)
    assert not any(f.severity == 'ERROR' for f in findings)
    record('unparsed-schema-file', 'R09', 'Registry validation accepts a referenced schema file containing invalid JSON.')

print(json.dumps({'meaning': 'Confirmed defects, not successful product acceptance tests', 'baseline': '22fc0e72f55fa68f98f5f9ffa92127e96c7b9913', 'results': results}, indent=2))
