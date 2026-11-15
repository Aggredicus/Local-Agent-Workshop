from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from workshop.hyperkanban import state as hk
from workshop.hyperkanban.validation import HyperKanbanError


def loaded(tmp_path):
    data = json.loads(Path('orchestration/hyperkanban/state.json').read_text())
    path = tmp_path / 'state.json'
    path.write_text(json.dumps(data))
    (tmp_path / 'packet.txt').write_text(hk.build_packet(data))
    return path, hk.load_state(path)


@pytest.mark.parametrize('bad', ['cycle', 'coordinate', 'evidence', 'boolean-byte', 'duplicate-dependency'])
def test_runtime_rejects_invalid_states(tmp_path, bad):
    _, data = loaded(tmp_path)
    card = data['cards'][0]
    if bad == 'cycle':
        card['deps'] = [card['id']]
    elif bad == 'coordinate':
        card['coords']['ring'] = 'wrong'
    elif bad == 'boolean-byte':
        card['byte'] = True
    elif bad == 'duplicate-dependency':
        data['cards'][1]['deps'] = [card['id'], card['id']]
    else:
        card.update(byte=8, test_contract={'required': True}, evidence_paths=[], open_exceptions=[])
        card['coords']['state'] = 'done'
    with pytest.raises(HyperKanbanError):
        hk.validate_state(data)


@pytest.mark.parametrize('path', ['missing.txt', '../outside.txt', '/etc/passwd'])
def test_completion_rejects_nonexistent_or_escaping_evidence(tmp_path, path):
    _, data = loaded(tmp_path)
    before = copy.deepcopy(data)
    with pytest.raises(HyperKanbanError, match='evidence'):
        hk.complete_card(data, data['cards'][0]['id'], evidence=[path], evidence_root=tmp_path)
    assert data == before


def test_completion_hashes_existing_contained_artifact(tmp_path):
    _, data = loaded(tmp_path)
    (tmp_path / 'result.txt').write_text('executed test report')
    completed = hk.complete_card(data, data['cards'][0]['id'], evidence=['result.txt'], evidence_root=tmp_path)
    assert len(completed['evidence_sha256']['result.txt']) == 64


def test_stale_writer_cannot_overwrite_newer_state(tmp_path):
    path, first = loaded(tmp_path)
    second = hk.load_state(path)
    first['project']['purpose'] = 'first writer'
    hk.save_state_and_packet(path, first)
    second['project']['purpose'] = 'stale second writer'
    with pytest.raises(HyperKanbanError, match='changed'):
        hk.save_state_and_packet(path, second)
    assert hk.load_state(path)['project']['purpose'] == 'first writer'


def test_packet_write_failure_is_recoverable_from_canonical_state(tmp_path, monkeypatch):
    path, data = loaded(tmp_path)
    data['project']['purpose'] = 'new canonical state'
    original = hk._atomic_write
    def fail_packet(target, content):
        if target.name == 'packet.txt':
            raise OSError('injected packet failure')
        return original(target, content)
    with monkeypatch.context() as patch:
        patch.setattr(hk, '_atomic_write', fail_packet)
        with pytest.raises(HyperKanbanError, match='state saved'):
            hk.save_state_and_packet(path, data)
    canonical = hk.load_state(path)
    assert canonical['project']['purpose'] == 'new canonical state'
    hk.save_packet(path, canonical)
    assert (tmp_path / 'packet.txt').read_text() == hk.build_packet(canonical)


def test_state_replace_failure_preserves_original_json(tmp_path, monkeypatch):
    path, data = loaded(tmp_path)
    original = path.read_bytes()
    data['project']['purpose'] = 'should not commit'
    def fail(*args):
        raise OSError('injected replace failure')
    monkeypatch.setattr(hk.os, 'replace', fail)
    with pytest.raises(OSError):
        hk.save_state(path, data)
    assert path.read_bytes() == original


def test_deleted_state_cannot_be_recreated_by_stale_writer(tmp_path):
    path, data = loaded(tmp_path)
    path.unlink()
    with pytest.raises(HyperKanbanError, match='changed'):
        hk.save_state(path, data)
    assert not path.exists()


def test_packet_cannot_be_built_from_uncommitted_mutations(tmp_path):
    path, data = loaded(tmp_path)
    original = (tmp_path / 'packet.txt').read_bytes()
    data['project']['name'] = 'uncommitted changes'
    with pytest.raises(HyperKanbanError, match='canonical'):
        hk.save_packet(path, data)
    assert (tmp_path / 'packet.txt').read_bytes() == original


@pytest.mark.parametrize('writer', [hk.save_state_and_packet, hk.save_packet])
def test_canonical_state_cannot_alias_derived_packet(tmp_path, writer):
    source, _ = loaded(tmp_path)
    packet = tmp_path / 'packet.txt'
    packet.write_bytes(source.read_bytes())
    state = hk.load_state(packet)
    original = packet.read_bytes()
    with pytest.raises(HyperKanbanError, match='alias'):
        writer(packet, state)
    assert packet.read_bytes() == original
