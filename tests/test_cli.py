import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from workshop import cli


def test_cli_main_exists():
    assert callable(cli.main)


def test_cli_main_without_args_prints_help(capsys):
    assert cli.main([]) == 0
    captured = capsys.readouterr()
    assert "Local Agent Workshop CLI" in captured.out
