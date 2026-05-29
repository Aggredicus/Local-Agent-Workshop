import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from workshop.cli import main
from workshop.hyperkanban.state import build_packet


STATE = Path("orchestration/hyperkanban/state.json")


def test_hk_validate_passes(capsys):
    assert main(["hk", "--state", str(STATE), "validate"]) == 0
    captured = capsys.readouterr()
    assert "HyperKanban validation passed" in captured.out


def test_hk_packet_prints_compact_packet(capsys):
    assert main(["hk", "--state", str(STATE), "packet"]) == 0
    captured = capsys.readouterr()
    assert captured.out.startswith("HK/0.1.0")
    assert "HK-001|03" in captured.out


def test_hk_list_prints_cards(capsys):
    assert main(["hk", "--state", str(STATE), "list"]) == 0
    captured = capsys.readouterr()
    assert "HK-001" in captured.out
    assert "Establish HyperKanban state kernel" in captured.out


def test_hk_show_prints_one_card(capsys):
    assert main(["hk", "--state", str(STATE), "show", "HK-002"]) == 0
    captured = capsys.readouterr()
    assert "HK-002" in captured.out
    assert "Add read-only HyperKanban CLI commands" in captured.out


def test_hk_show_unknown_card_fails(capsys):
    assert main(["hk", "--state", str(STATE), "show", "HK-999"]) == 1
    captured = capsys.readouterr()
    assert "unknown card id" in captured.err


def test_hk_next_returns_active_root_card(capsys):
    assert main(["hk", "--state", str(STATE), "next"]) == 0
    captured = capsys.readouterr()
    assert "HK-001" in captured.out


def write_mutable_state(tmp_path, *, evidence_required=True):
    state = json.loads(STATE.read_text(encoding="utf-8"))
    card = state["cards"][0]
    card["test_contract"] = {"required": evidence_required, "commands": ["python -m pytest"]}
    card["doc_contract"] = {"required": False, "targets": []}
    state_path = tmp_path / "state.json"
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    (tmp_path / "packet.txt").write_text(build_packet(state), encoding="utf-8")
    return state_path


def test_hk_complete_requires_evidence_for_contracted_card(tmp_path, capsys):
    state_path = write_mutable_state(tmp_path)
    assert main(["hk", "--state", str(state_path), "complete", "HK-001"]) == 1
    captured = capsys.readouterr()
    assert "requires evidence" in captured.err


def test_hk_complete_records_evidence_and_updates_packet(tmp_path, capsys):
    state_path = write_mutable_state(tmp_path)
    assert main(["hk", "--state", str(state_path), "complete", "HK-001", "--evidence", "tests/test_hyperkanban_cli.py"]) == 0
    captured = capsys.readouterr()
    assert "Completed HK-001" in captured.out

    state = json.loads(state_path.read_text(encoding="utf-8"))
    card = state["cards"][0]
    assert card["coords"]["state"] == "done"
    assert card["byte"] & 8
    assert "tests/test_hyperkanban_cli.py" in card["evidence_paths"]
    assert (tmp_path / "packet.txt").read_text(encoding="utf-8") == build_packet(state)


def test_hk_complete_allows_review_exception(tmp_path, capsys):
    state_path = write_mutable_state(tmp_path)
    assert main(["hk", "--state", str(state_path), "complete", "HK-001", "--exception", "review-card:RC-001"]) == 0
    captured = capsys.readouterr()
    assert "Completed HK-001" in captured.out
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert "review-card:RC-001" in state["cards"][0]["open_exceptions"]
