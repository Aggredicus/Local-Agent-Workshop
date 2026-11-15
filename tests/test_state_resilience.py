"""Large dependency graphs and corrupt derived packets fail predictably."""
import json
import os
from pathlib import Path

import pytest

from workshop.cli import main
from workshop.doctor import run_doctor
from workshop.hyperkanban.state import build_packet
from workshop.hyperkanban.validation import validate_dependencies


def graph(count):
    return {str(i): {'deps': [str(i+1)] if i < count-1 else []} for i in range(count)}


def test_large_valid_dependency_chain_does_not_exhaust_python_stack():
    validate_dependencies(graph(2000))


def test_large_cycle_has_bounded_actionable_diagnostic():
    cards = graph(2000)
    cards['1999']['deps'] = ['0']
    with pytest.raises(ValueError, match='cycle') as error:
        validate_dependencies(cards)
    assert len(str(error.value)) < 512


def test_all_three_node_graphs_agree_with_independent_dependency_resolution():
    # Exhaustive comparison against fixed-point resolution catches disconnected
    # cycles as well as connected ones, without copying the DFS implementation.
    for mask in range(1 << 9):
        cards = {str(i): {'deps': [str(j) for j in range(3) if mask & (1 << (i*3+j))]} for i in range(3)}
        resolved = set()
        while True:
            next_resolved = {key for key, card in cards.items() if set(card['deps']) <= resolved}
            if next_resolved <= resolved:
                break
            resolved |= next_resolved
        try:
            validate_dependencies(cards)
        except ValueError:
            rejected = True
        else:
            rejected = False
        assert rejected == (len(resolved) != 3), f'Graph {mask} disagrees'


def test_invalid_packet_encoding_is_reported_and_repair_preserves_state(tmp_path, capsys):
    source = Path('orchestration/hyperkanban/state.json').read_bytes()
    folder = tmp_path / 'orchestration/hyperkanban'
    folder.mkdir(parents=True)
    path = folder / 'state.json'
    path.write_bytes(source)
    packet = folder / 'packet.txt'
    packet.write_bytes(b'\xff')
    assert main(['hk', '--state', str(path), 'validate']) == 1
    assert 'packet' in capsys.readouterr().err
    assert any(c.name == 'hyperkanban' and c.level == 'FAIL' for c in run_doctor(tmp_path))
    assert main(['hk', '--state', str(path), 'repair-packet']) == 0
    assert path.read_bytes() == source
    assert packet.read_text() == build_packet(json.loads(source))


@pytest.mark.parametrize('target_name', ['state.json', 'packet.txt'])
@pytest.mark.parametrize('kind', ['link', 'fifo'])
def test_state_readers_reject_links_and_special_files_without_opening_them(tmp_path, capsys, monkeypatch, target_name, kind):
    source = Path('orchestration/hyperkanban/state.json').read_bytes()
    state = tmp_path / 'state.json'
    state.write_bytes(source)
    (tmp_path / 'packet.txt').write_text(build_packet(json.loads(source)))
    target = tmp_path / target_name
    target.unlink()
    if kind == 'fifo':
        os.mkfifo(target)
    else:
        private = tmp_path / 'private'
        private.write_text('PRIVATE_STATE_CANARY')
        target.symlink_to(private)
    for method in ('read_text', 'read_bytes'):
        original = getattr(Path, method)
        def reject(path, *args, _original=original, **kwargs):
            if path == target:
                pytest.fail('Reader attempted to open an unsafe state or packet file')
            return _original(path, *args, **kwargs)
        monkeypatch.setattr(Path, method, reject)
    assert main(['hk', '--state', str(state), 'validate']) == 1
    out = capsys.readouterr()
    assert 'PRIVATE_STATE_CANARY' not in out.out + out.err
