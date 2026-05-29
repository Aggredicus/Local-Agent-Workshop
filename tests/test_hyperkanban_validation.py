import copy
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_hyperkanban as hk


def write_state(tmp_path, state, packet=True):
    folder = tmp_path / "hyperkanban"
    folder.mkdir()
    state_path = folder / "state.json"
    state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    if packet:
        (folder / "packet.txt").write_text(hk.build_packet(state), encoding="utf-8")
    return state_path


def base_state():
    return {
        "schema_version": "0.1.0",
        "project": {"name": "Test Project", "purpose": "Validate HyperKanban."},
        "rank": 3,
        "axes": [
            {"key": "ring", "name": "Ring", "type": "integer", "default": 0, "values": [0, 1, 2], "role": "depth"},
            {"key": "state", "name": "State", "type": "enum", "default": "backlog", "values": ["backlog", "active", "done"], "role": "workflow"},
            {"key": "risk", "name": "Risk", "type": "enum", "default": "none", "values": ["none", "medium"], "role": "safety"},
        ],
        "cards": [
            {
                "id": "HK-001",
                "title": "Root",
                "desc": "Root card",
                "deps": [],
                "coords": {"ring": 0, "state": "active", "risk": "medium"},
                "byte": 3,
                "tags": ["root"],
            },
            {
                "id": "HK-002",
                "title": "Child",
                "desc": "Child card",
                "deps": ["HK-001"],
                "coords": {"ring": 1, "state": "backlog", "risk": "none"},
                "byte": 4,
                "tags": ["child"],
            },
        ],
        "rules": [],
    }


def test_valid_state_passes(tmp_path):
    state_path = write_state(tmp_path, base_state())
    hk.validate_state(state_path)


def test_missing_dependency_fails(tmp_path):
    state = base_state()
    state["cards"][1]["deps"] = ["HK-999"]
    state_path = write_state(tmp_path, state)
    try:
        hk.validate_state(state_path)
    except ValueError as exc:
        assert "missing card" in str(exc)
    else:
        raise AssertionError("missing dependency should fail")


def test_dependency_cycle_fails(tmp_path):
    state = base_state()
    state["cards"][0]["deps"] = ["HK-002"]
    state_path = write_state(tmp_path, state)
    try:
        hk.validate_state(state_path)
    except ValueError as exc:
        assert "cycle" in str(exc)
    else:
        raise AssertionError("dependency cycle should fail")


def test_invalid_byte_fails(tmp_path):
    state = base_state()
    state["cards"][0]["byte"] = 999
    state_path = write_state(tmp_path, state)
    try:
        hk.validate_state(state_path)
    except ValueError as exc:
        assert "byte" in str(exc)
    else:
        raise AssertionError("invalid byte should fail")


def test_invalid_coord_value_fails(tmp_path):
    state = base_state()
    state["cards"][0]["coords"]["state"] = "invalid"
    state_path = write_state(tmp_path, state)
    try:
        hk.validate_state(state_path)
    except ValueError as exc:
        assert "invalid value" in str(exc)
    else:
        raise AssertionError("invalid coordinate should fail")


def test_unknown_coord_axis_fails(tmp_path):
    state = base_state()
    state["cards"][0]["coords"]["unknown"] = "value"
    state_path = write_state(tmp_path, state)
    try:
        hk.validate_state(state_path)
    except ValueError as exc:
        assert "unknown axes" in str(exc)
    else:
        raise AssertionError("unknown coordinate axis should fail")


def test_packet_drift_fails(tmp_path):
    state = base_state()
    state_path = write_state(tmp_path, state)
    (state_path.parent / "packet.txt").write_text("stale packet\n", encoding="utf-8")
    try:
        hk.validate_state(state_path)
    except ValueError as exc:
        assert "packet out of sync" in str(exc)
    else:
        raise AssertionError("packet drift should fail")
