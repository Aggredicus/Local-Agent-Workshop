import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from workshop.cli import main


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
